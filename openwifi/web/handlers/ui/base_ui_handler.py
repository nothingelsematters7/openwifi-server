#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import pystache

import openwifi.static
import openwifi.web.handlers.base_handler


class BaseUiHandler(openwifi.web.handlers.base_handler.BaseHandler):
    """
    Base request handler for user interface.
    """

    _renderer = pystache.Renderer(
        file_encoding="utf-8",
        string_encoding="utf-8",
        search_dirs=[
            os.path.join(os.path.dirname(openwifi.static.__file__), "templates"),
        ],
        file_extension="mustache",
    )