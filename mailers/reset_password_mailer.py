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

from aaa_onboarding_portal.mailers.mailer import Mailer


class ResetPasswordMailer(Mailer):

    def __init__(self, reset):
        super(self.__class__, self).__init__()
        reset.check_valid()
        self.to = reset.email
        self.subject = "FreeIPA Community Portal: Reset Password"
        self.template = "reset_password_email.txt"
        self.template_opts = {'reset_info': reset}
