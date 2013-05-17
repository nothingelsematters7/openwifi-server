#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.client
import logging

import openwifi.web.handlers.base_handler


class BaseHandler(openwifi.web.handlers.base_handler.BaseHandler):
    """
    Base request handler for API.
    """

    _CONTENT_TYPE_HEADER = "Content-Type"
    _X_CLIENT_ID_HEADER = "X-Client-ID"

    def initialize(self):
        super(BaseHandler, self).initialize()

        self._logger = logging.getLogger(BaseHandler.__name__)

    def prepare(self):
        super(BaseHandler, self).prepare()

        # Validate client ID.
        self._client_id = self.request.headers.get(self._X_CLIENT_ID_HEADER)
        self._logger.debug("%s: %s", self._X_CLIENT_ID_HEADER, self._client_id)

        self.set_header("Content-Type", "application/json")
