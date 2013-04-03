#!/usr/env/bin python3
# -*- coding: utf-8 -*-

import os
import pystache
import openwifi.static.templates
import openwifi.web

import openwifi.web.handlers.base_handler


class BaseUiHandler(openwifi.web.handlers.base_handler.BaseHandler):
    """
    Base request handler for user interface.
    """

    _renderer = pystache.Renderer(
        file_encoding="utf-8",
        string_encoding="utf-8",
        search_dirs=[os.path.dirname(openwifi.static.templates.__file__)],
        file_extension="mustache",
    )