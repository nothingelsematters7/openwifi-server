#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

import openwifi.__version__
import openwifi.web.handlers.api.base_handler


class InfoHandler(openwifi.web.handlers.api.base_handler.BaseHandler):
	"""
	Gets the API info.
	"""

    def get(self, *args, **kwargs):
        self.write(json.dumps({
            "version": openwifi.__version__.version,
        }))
