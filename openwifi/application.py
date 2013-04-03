#!/usr/env/bin python3
# -*- coding: utf-8 -*-

import logging

import tornado.ioloop

import openwifi.helpers.exit_codes
import openwifi.web.web_application


class Application:
    """
    Open WiFi Server application.
    """

    def __init__(self):
        self._logger = logging.getLogger(Application.__name__)

    def main(self, args):
        self._logger.info("Listening on port %s.", args.port)
        openwifi.web.web_application.WebApplication().listen(args.port)
        try:
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            self._logger.info("Keyboard interrupt.")
            return openwifi.helpers.exit_codes.EX_OK