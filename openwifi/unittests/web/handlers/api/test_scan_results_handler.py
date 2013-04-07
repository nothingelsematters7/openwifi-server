#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from openwifi.web.handlers.api.scan_results_handler import (
    _validate_bssid,
)


class TestScanResultsHandler(unittest.TestCase):
    def test_validate_bssid_positive(self):
        self.assertTrue(_validate_bssid("02:29:e9:87:78:86"))

    def test_validate_bssid_negative(self):
        self.assertFalse(_validate_bssid("02:29:e9:87:78:8r"))