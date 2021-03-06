# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org>
#               2019 TurnKey GNU/Linux <admin@turnkeylinux.org>
#
# turnkey-conffile is open source software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.

import os


class ConfFileError(Exception):
    pass


class ConfFile(dict):
    """Configuration file class (targeted at simple shell type configs)

    Usage:

        class foo(ConfFile):
            CONF_FILE = /path/to/conf
            REQUIRED = ['arg1' ,'arg2']

        conf = foo()
        print conf.arg1     # display ARG1 value from /path/to/conf
        conf.arg2 = value   # set ARG2 value
        conf.write()        # write new/update config to /path/to/conf

    Format:

        # comments are ignored
        NAME=alon
        AGE=29

    """
    CONF_FILE = None
    REQUIRED = []
    SET_ENVIRON = False

    def __init__(self):
        self.read()
        self.validate_required()
        if self.SET_ENVIRON:
            self.set_environ()

    def validate_required(self, required=[]):
        """raise exception if required arguments are not set
        REQUIRED validated by default, but can be optionally extended
        """
        self.REQUIRED.extend(required)
        for attr in self.REQUIRED:
            if attr not in self:
                error = "%s not specified in %s" % (attr.upper(),
                                                    self.CONF_FILE)
                raise ConfFileError(error)

    def set_environ(self):
        """set environment (run on initialization if SET_ENVIRON)"""
        for key, val in list(self.items()):
            os.environ[key.upper()] = val

    def read(self):
        if not self.CONF_FILE or not os.path.exists(self.CONF_FILE):
            return

        with open(self.CONF_FILE) as fob:
            for line in fob:
                line = line.rstrip()
                if not line or line.startswith("#"):
                    continue

                key, val = line.split("=")
                self[key.strip().lower()] = val.strip()

    def write(self):
        with open(self.CONF_FILE, "w") as fob:
            items = list(self.items())
            items.sort()
            for key, val in items:
                print("%s=%s" % (key.upper(), val), file=fob)

    def items(self):
        items = []
        for key in self:
            items.append((key, self[key]))

        return items

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, key, val):
        self[key] = val
