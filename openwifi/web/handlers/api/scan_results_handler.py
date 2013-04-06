#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openwifi.web.handlers.api.base_handler


class ScanResultsHandler(openwifi.web.handlers.api.base_handler.BaseHandler):
    """
    Scan results request handler.
    """

    def initialize(self, db):
        self._db = db

    def put(self, *args, **kwargs):
        """
        Puts the scan result.
        """

        pass