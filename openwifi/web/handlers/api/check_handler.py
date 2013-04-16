#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openwifi.web.handlers.api.base_handler


class CheckHandler(openwifi.web.handlers.api.base_handler.BaseHandler):
    """
    Used by the client to check the Internet connectivity.
    """

    def get(self, *args, **kwargs):
        # Should write nothing.
        pass