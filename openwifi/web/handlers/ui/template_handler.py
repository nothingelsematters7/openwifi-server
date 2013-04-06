#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import tornado.locale
import tornado.web

import openwifi.web.handlers.ui.base_ui_handler


class TemplateHandler(openwifi.web.handlers.ui.base_ui_handler.BaseUiHandler):
    """
    Request handler that renders a template.
    """

    def __init__(self, application, request, template_name, **kwargs):
        super(TemplateHandler, self).__init__(
            application,
            request,
            **kwargs
        )

        self._logger = logging.getLogger(TemplateHandler.__name__)
        self._template_name = template_name

    @tornado.web.removeslash
    def get(self, *args, **kwargs):
        self._logger.debug("Request locale: %s", self.locale.code)
        self.write(self._renderer.render_name(
            self._template_name,
            # Translate function.
            t=self.locale.translate,
        ))