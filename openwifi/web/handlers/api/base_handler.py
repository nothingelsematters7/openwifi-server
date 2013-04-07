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

    _OK_RESPONSE = "OK"

    def initialize(self):
        super(BaseHandler, self).initialize()

        self._logger = logging.getLogger(BaseHandler.__name__)

    def prepare(self):
        super(BaseHandler, self).prepare()

        headers = self.request.headers
        self._client_id = headers.get(self._X_CLIENT_ID_HEADER)

        if (
            headers.get(self._CONTENT_TYPE_HEADER) != "application/json"
        ):
            self._logger.warning("Bad headers.")
            self.send_error(status_code=http.client.BAD_REQUEST)
            return

        self._logger.debug("Client ID: %s", self._client_id)