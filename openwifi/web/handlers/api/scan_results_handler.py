#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.client
import json
import logging

import openwifi.web.handlers.api.base_handler


class ScanResultsHandler(openwifi.web.handlers.api.base_handler.BaseHandler):
    """
    Scan results request handler.
    """

    # noinspection PyMethodOverriding
    def initialize(self, db):
        super(ScanResultsHandler, self).initialize()

        self._db = db
        self._logger = logging.getLogger(ScanResultsHandler.__name__)

    def prepare(self):
        super(ScanResultsHandler, self).prepare()

        pass

    def put(self, *args, **kwargs):
        """
        Puts the scan result.
        """

        try:
            scan_result = self.request.body.decode("utf-8")
            scan_result = json.loads(scan_result)
        except ValueError:
            self._logger.warning("Value error.")
            self.send_error(status_code=http.client.BAD_REQUEST)
            return

        self._logger.debug("Got scan result: %s", scan_result)
