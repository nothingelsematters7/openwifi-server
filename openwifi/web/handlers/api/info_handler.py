#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

import openwifi.__version__
import openwifi.web.handlers.api.base_handler


class InfoHandler(openwifi.web.handlers.api.base_handler.BaseHandler):
    # noinspection PyMethodOverriding
    def initialize(self, test_mode):
        super(InfoHandler, self).initialize()

        self._test_mode = test_mode

    def get(self, *args, **kwargs):
        self.write(json.dumps({
            "version": openwifi.__version__.version,
            "test_mode": self._test_mode,
        }))