#!/usr/bin/python

import cherrypy

from aaa_onboarding_portal import portalapp
from aaa_onboarding_portal.config import config

config.load(config.deployment_config)

application = cherrypy.Application(
    portalapp.app(),
    script_name=None,
    config=portalapp.conf
)
