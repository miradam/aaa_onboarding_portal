# Authors:
#   Adam Heczko, Mirantis inc.
#
# Copyright (C) 2017 Mirantis inc.
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
The main web server for the AAA onboarding portal.
"""

import os

import cherrypy

import jinja2

from aaa_onboarding_portal import PACKAGE_DATA_DIR
from aaa_onboarding_portal.config import config
from aaa_onboarding_portal.mailers.reset_password_mailer import ResetPasswordMailer
from aaa_onboarding_portal.mailers.sign_up_mailer import SignUpMailer
from aaa_onboarding_portal.model.password_reset import PasswordReset
from aaa_onboarding_portal.model.user import User


TEMPLATE_ENV = jinja2.Environment(
    loader=jinja2.PackageLoader('aaa_onboarding_portal', 'templates'))


class SelfServicePortal(object):
    """The class for all bare pages which don't require REST logic
    """

    @cherrypy.expose
    def index(self):  # pylint: disable=no-self-use
        """/index"""
        return render("layout.html")

    @cherrypy.expose
    def complete(self):  # pylint: disable=no-self-use
        """/complete"""
        # pylint: disable=no-member
        return render('complete.html')


class SelfServiceUserRegistration(object):
    """Class for self-service user registration, which requires REST features
    """
    exposed = True

    def GET(self):  # pylint: disable=invalid-name
        """GET /new_user"""
        return self._render_registration_form()

    def POST(self, **kwargs):  # pylint: disable=invalid-name
        """POST /new_user"""
        user = User(kwargs)
        #errors = check_captcha(kwargs)
        errors = ""
        if not errors:
            errors = user.save()
        if not errors:
            # email the admin that the user has signed up
            SignUpMailer(user).mail()
            raise cherrypy.HTTPRedirect('/complete')
        return self._render_registration_form(user, errors)

    def _render_registration_form(self, user=User(), errors=None):  # pylint: disable=no-self-use
        """renders the registration form. private."""
        # pylint: disable=no-member
        # captcha = CaptchaHelper()

        # return render('new_user.html', user=user, errors=errors, captcha=captcha)
        return render('new_user.html', user=user, errors=errors)      

class RequestAccess(object):
    """Handles requesting a password reset

    GET, POST /request_access
    """
    exposed = True

    def GET(self):
        """returns the request form"""
        # captcha = CaptchaHelper()
        # return render('request_access.html', captcha=captcha)
        return render('request_access.html')

    def POST(self, **kwargs):
        """accepts a username and initiates a reset"""
        # errors = check_captcha(kwargs)
        if not errors and not kwargs['username']:
            errors = "Username is required"
        if errors:
            # return render('request_access.html', errors=errors, captcha=CaptchaHelper())
            return render('request_access.html', errors=errors)
        r = PasswordReset(kwargs['username'])
        r.save()
        if r.check_valid():
            ResetPasswordMailer(r).mail()
        raise cherrypy.HTTPRedirect('/complete')


class ApproveAccess(object):
    """Handles the actual reset of the password

    GET, POST /approve_access
    """
    exposed = True

    def GET(self, **params):
        """Renders the reset request form.

        if username and/or token are supplied in the querystring, pre-fills the
        form for the user
        """
        username = params.get('username', '')
        token = params.get('token', '')
        return render('approve_access.html', username=username, token=token)

    def POST(self, **params):
        if 'username' not in params or 'token' not in params:
            return render('approve_access.html',
                          username=params.get('username', ''),
                          token=params.get('token', ''),
                          error='All fields are required'
                          )
        else:
            p = PasswordReset.load(params['username'])
            if p is not None and p.token == params['token']:
                new_pass = p.reset_password()
                PasswordReset.expire(params['username'])
                return render('display_password.html', password=new_pass)
            else:
                PasswordReset.expire(params['username'])
                return render('invalid_token.html')

class ManageAccess(object):
    """Handles the actual reset of the password

    GET, POST /manage_access
    """
    exposed = True

    def GET(self, **params):
        """Renders the reset request form.

        if username and/or token are supplied in the querystring, pre-fills the
        form for the user
        """
        username = params.get('username', '')
        token = params.get('token', '')
        return render('manage_access.html', username=username, token=token)

    def POST(self, **params):
        if 'username' not in params or 'token' not in params:
            return render('manage_access.html',
                          username=params.get('username', ''),
                          token=params.get('token', ''),
                          error='All fields are required'
                          )
        else:
            p = PasswordReset.load(params['username'])
            if p is not None and p.token == params['token']:
                new_pass = p.reset_password()
                PasswordReset.expire(params['username'])
                return render('display_password.html', password=new_pass)
            else:
                PasswordReset.expire(params['username'])
                return render('invalid_token.html')


def render(template, **args):
    return TEMPLATE_ENV.get_template(template).render(**args)

'''
def check_captcha(args):
    if not check_response(args['response'], args['solution']):
        return "Incorrect Captcha response"
    else:
        return None
'''

conf = {
    '/assets': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(PACKAGE_DATA_DIR, 'assets'),
    },
    '/new_user': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        # 'tools.response_headers.headers': [('Content-Type', 'text/plain')]
    },
    '/request_access': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
    },
    '/approve_access': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
    },
    '/manage_access': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
    }
}



def app():
    """Main entry point for the web application. If you run this library as a
    standalone application, you can just use this function
    """
    if not config:
        raise ValueError('Run config.load(configfile) first!')

    webapp = SelfServicePortal()
    webapp.new_user = SelfServiceUserRegistration(
    )  # pylint: disable=attribute-defined-outside-init
    webapp.request_access = RequestAccess()
    webapp.approve_access = ApproveAccess()
    webapp.manage_access = ManageAccess()
    return webapp
