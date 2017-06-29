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
"""Entry point for development server

Copy your keytab to ./var/portal.keytab and run::

    python2.7 -m aaa_onboarding_portal

"""
import cherrypy

from aaa_onboarding_portal import portalapp
from aaa_onboarding_portal.config import config

config.load(config.development_config)

# 8080 is occupied by Dogtag
cherrypy.config.update({
    'server.socket_host': '127.0.0.1',
    'server.socket_port': 10080,
})

cherrypy.quickstart(
    portalapp.app(),
    '/',
    app.conf
)
