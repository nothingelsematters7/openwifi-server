#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# noinspection PyPackageRequirements
import bson.objectid
import requests

import openwifi.integration_tests


class TestScanResultsHandler(openwifi.integration_tests.BaseTestCase):
    _URL = openwifi.integration_tests.BaseTestCase._BASE_URL + "scan-results/"

    def test_post(self):
        response = requests.post(self._URL, json.dumps({
            "bssid": "00:00:00:00:00:00",
            "ssid": "test",
            "ts": 1,
            "acc": 10.0,
            "loc": {
                "lat": 53.87,
                "lon": 27.54,
            },
        }))
        self.assertEqual(200, response.status_code, "Request failed.")
        # Validate ObjectID.
        bson.objectid.ObjectId(response.json())

    def test_get(self):
        response = requests.get(self._URL + "000000000000000000000000/1/")
        self.assertEqual(200, response.status_code, "Request failed.")
        obj = response.json()
        self.assertIsInstance(obj, list, "Response object is not a list.")
        self.assertTrue(obj, "The list is empty.")