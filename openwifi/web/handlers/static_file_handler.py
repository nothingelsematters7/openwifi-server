#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web


class StaticFileHandler(tornado.web.StaticFileHandler):
    """
    StaticFileHandler wrapper. Improves Page Speed.
    """

    _CACHE_TIME = 60 * 60 * 24 * 10

    def get_cache_time(self, path, modified, mime_type):
        """
        Gets cache time in seconds.
        """
        return self._CACHE_TIME

    def set_extra_headers(self, path):
        self.set_header("Vary", "Accept-Encoding")
        # Tell browser that our JSON is UTF-8 encoded.
        if path.endswith(".json"):
            self.set_header("Content-Type", "application/json; charset=UTF-8")