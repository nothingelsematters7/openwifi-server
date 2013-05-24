#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import tornado.locale
import tornado.web

import openwifi.helpers
import openwifi.web.handlers.ui.base_handler


class TemplateHandler(openwifi.web.handlers.ui.base_handler.BaseHandler):
    """
    Request handler that renders a template.
    """

    # noinspection PyMethodOverriding
    def initialize(self, db, template_name):
        super(TemplateHandler, self).initialize()

        self._logger = logging.getLogger(TemplateHandler.__name__)
        self._template_name = template_name
        self._db = db

    def prepare(self):
        super(TemplateHandler, self).prepare()

        self._logger.debug("User agent: %s", self.request.headers.get("User-Agent"))

    @tornado.web.removeslash
    def get(self, *args, **kwargs):
        self._logger.debug("Request locale: %s", self.locale.code)
        self.write(self._renderer.render_name(
            self._template_name,
            # Translate function.
            t=self.locale.translate,
            statistics=openwifi.helpers.Statistics(self._db),
        ))
