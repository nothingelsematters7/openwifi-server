#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

import tornado.web

import openwifi.web.handlers.api.info_handler
import openwifi.web.handlers.api.scan_results_handler
import openwifi.web.handlers.static_file_handler
import openwifi.web.handlers.ui.template_handler
import openwifi.static
import openwifi.web


class WebApplication(tornado.web.Application):
    def __init__(self, db, test_mode=False):
        static_files_path = os.path.abspath(os.path.dirname(openwifi.static.__file__))

        super(WebApplication, self).__init__(
            handlers=[(
                r"/",
                openwifi.web.handlers.ui.template_handler.TemplateHandler,
                {"template_name": "home"},
            ), (
                r"/(robots.txt)",
                openwifi.web.handlers.static_file_handler.StaticFileHandler,
                {"path": static_files_path},
            ), (
                r"/(favicon\.(ico|png))",
                openwifi.web.handlers.static_file_handler.StaticFileHandler,
                {"path": os.path.join(static_files_path, "ico")}
            ), (
                r"/static/(.*)",
                openwifi.web.handlers.static_file_handler.StaticFileHandler,
                {"path": static_files_path},
            ), (
                r"/api/scan-results/",
                openwifi.web.handlers.api.scan_results_handler.ScanResultsHandler,
                {"db": db},
            ), (
                r"/api/scan-results/(\d+)/(\d+)/",
                openwifi.web.handlers.api.scan_results_handler.ScanResultsHandler,
                {"db": db},
            ), (
                r"/api/info/",
                openwifi.web.handlers.api.info_handler.InfoHandler,
                {"test_mode": test_mode}
            )],
            gzip=True,
        )

        self._logger = logging.getLogger(WebApplication.__name__)

    def log_request(self, handler):
        """
        Overrides the default function in order to customize log messages.
        """

        if "log_function" in self.settings:
            self.settings["log_function"](handler)
            return
        if handler.get_status() < 400:
            log_method = self._logger.debug
        elif handler.get_status() < 500:
            log_method = self._logger.warning
        else:
            log_method = self._logger.error
        request_time = 1000.0 * handler.request.request_time()
        log_method(
            "%d %s %.2fms",
            handler.get_status(),
            handler._request_summary(),
            request_time,
        )