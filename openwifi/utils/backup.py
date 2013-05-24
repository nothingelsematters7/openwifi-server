#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Backup service utility.
"""

import openwifi.helpers.exit_codes


class Backup:
    """
    Backup utility main class.
    """

    def __init__(self):
        self._logger = logging.getLogger(Backup.__name__)

    def main(self, args):
        return openwifi.helpers.exit_codes.EX_OK
