#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

import requests

import openwifi.integration_tests


class TestScanResultsHandler(openwifi.integration_tests.BaseTestCase):
    _URL = openwifi.integration_tests.BaseTestCase._BASE_URL + "scan-results/"

    def test_post(self):
        response = requests.post(self._URL, json.dumps({
            "bssid": "00:00:00:00:00:00",
        }))
        self.assertEqual("OK", response.json().get("r"))