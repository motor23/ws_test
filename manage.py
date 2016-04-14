#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import os
import sys
from importlib import import_module
import pwd
import logging
import warnings
import admin.cfg

import iktomi
from iktomi.cli import manage
from iktomi.cli.base import Cli
from iktomi.utils import cached_property



class deferred_command(Cli):
    def __init__(self, func):
        self.get_digest = func

    @cached_property
    def digest(self):
        return self.get_digest()

    def description(self, *args, **kwargs):
        return self.digest.description(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.digest(*args, **kwargs)


@deferred_command
def ws_admin_command():
    from admin_app.servers.websockets import WS_Server
    import admin.cfg
    from admin.ws_app import WS_App
    server = WS_Server(admin.cfg.WS_SERVER_URL, WS_App())
    server.serve_forever()


def run():
    manage(dict(
        ws_admin=ws_admin_command,
    ), sys.argv)


def config_logging():
    logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    config_logging()
    if not os.getuid():
        try:
            os.setgroups([])
            p = pwd.getpwnam(admin.cfg.UID)
            uid = p[2]
            gid = p[3]
            os.setgid(gid)
            os.setegid(gid)
            os.setuid(uid)
            os.seteuid(uid)
        except AttributeError:
            sys.exit('UID and GID configuration variables are required '\
                     'when is launched as root')
    run()
