#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

import tornado.httpserver
import tornado.ioloop
import tornado.locale

import openwifi.helpers.exit_codes
import openwifi.static
import openwifi.web.web_application


class Application:
    """
    Open WiFi Server application.
    """

    def __init__(self):
        self._logger = logging.getLogger(Application.__name__)

    def main(self, args):
        web_application = openwifi.web.web_application.WebApplication()

        # Set up HTTP server.
        self._logger.info("HTTP port %s.", args.http_port)
        http_server = tornado.httpserver.HTTPServer(web_application)
        http_server.listen(args.http_port)
        # Set up HTTPS server if possible.
        application_path = os.path.dirname(__file__)
        certificate_path, key_path = (
            os.path.join(application_path, "cacert.pem"),
            os.path.join(application_path, "privkey.pem"),
        )
        if certificate_path and key_path:
            https_server = tornado.httpserver.HTTPServer(
                web_application,
                ssl_options={
                    "certfile": certificate_path,
                    "keyfile": key_path,
                },
            )
            self._logger.info("HTTPS port: %s.", args.https_port)
            https_server.listen(args.https_port)
        else:
            self._logger.info("Not using HTTPS.")
        # Load translations.
        self._logger.info("Loading translations ...")
        tornado.locale.load_translations(
            os.path.join(os.path.dirname(openwifi.static.__file__), "translations"),
        )
        tornado.locale.set_default_locale("en")
        # Start I/O loop.
        self._logger.info("I/O loop is being started.")
        try:
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            self._logger.info("Keyboard interrupt.")
            return openwifi.helpers.exit_codes.EX_OK