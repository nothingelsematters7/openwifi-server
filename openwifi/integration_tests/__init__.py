#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import requests

import openwifi.__version__


class BaseTestCase(unittest.TestCase):
    _BASE_URL = "http://localhost:8080/api/"
    _URL = _BASE_URL + "info/"

    @classmethod
    def setUpClass(cls):
        try:
            response = requests.get(BaseTestCase._URL)
        except requests.exceptions.ConnectionError as ex:
            raise ValueError("The API is not found.") from ex
        info = response.json()
        if not info.get("test_mode"):
            raise ValueError("The API is not running in test mode.")
        if info.get("version") != openwifi.__version__.version:
            raise ValueError("Invalid API version.")