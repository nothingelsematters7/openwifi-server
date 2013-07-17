#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys

import pymongo
import pymongo.database

import redis

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
        # Initializing the database connection.
        self._logger.info("Connecting to the database ...")
        mongo_client = pymongo.MongoClient()
        db = pymongo.database.Database(mongo_client, args.database_name)
        self._logger.info("Creating indexes ...")
        db.scan_results.ensure_index([
            # For server-to-client synchronization.
            ("_id", pymongo.ASCENDING),
        ])
        db.scan_results.ensure_index([
            # For fast checking if the scan result already exists.
            ("cid", pymongo.ASCENDING),
            ("ts", pymongo.ASCENDING),
            ("bssid", pymongo.ASCENDING),
        ], unique=True)
        db.scan_results.ensure_index([
            # For micro-synchronization feature.
            ("loc", pymongo.GEO2D),
        ])
        # Initializing the cache.
        cache = redis.StrictRedis()
        # Initializing the web application.
        self._logger.info("Initializing the web application ...")
        web_application = openwifi.web.web_application.WebApplication(
            db,
            cache,
            enable_gzip=args.enable_gzip,
        )
        # Set up HTTP server.
        self._logger.info("HTTP port %s.", args.http_port)
        http_server = tornado.httpserver.HTTPServer(web_application)
        http_server.listen(args.http_port, address="127.0.0.1")
        # Set up HTTPS server if possible.
        application_path = os.path.abspath(os.path.dirname(__file__))
        certificate_path, key_path = (
            os.path.join(application_path, "cacert.pem"),
            os.path.join(application_path, "privkey.pem"),
        )
        if args.https_port and certificate_path and key_path:
            https_server = tornado.httpserver.HTTPServer(
                web_application,
                ssl_options={
                    "certfile": certificate_path,
                    "keyfile": key_path,
                },
            )
            self._logger.info("HTTPS port: %s.", args.https_port)
            https_server.listen(args.https_port, address="127.0.0.1")
        else:
            self._logger.info("Not using HTTPS.")
        # Load translations.
        self._logger.info("Loading translations ...")
        tornado.locale.load_translations(
            os.path.join(os.path.dirname(openwifi.static.__file__), "translations"),
        )
        tornado.locale.set_default_locale("en")
        # Fork if requested.
        if args.fork:
            self._fork()
        # Start I/O loop.
        self._logger.info("I/O loop is being started.")
        try:
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            self._logger.info("Keyboard interrupt.")
            return openwifi.helpers.exit_codes.EX_OK

    def _fork(self):
        # Do the first fork.
        if os.fork():
            self._logger.info("Exiting because of fork.")
            sys.exit(openwifi.helpers.exit_codes.EX_OK)
        # Decouple from parent environment.
        os.chdir("/")
        os.setsid()
        os.umask(0)
        # Do the second fork.
        pid = os.fork()
        if pid:
            self._logger.info("Exiting because of fork.")
            self._logger.info("PID: %s", pid)
            sys.exit(openwifi.helpers.exit_codes.EX_OK)
        # Done.
        self._logger.info("Forked.")
