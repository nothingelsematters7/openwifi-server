#!/usr/env/bin python3
# -*- coding: utf-8 -*-

"""
Helper classes and functions.
"""

import json
import logging
import time

# noinspection PyPackageRequirements
import bson.objectid


class MongoEncoder(json.JSONEncoder):
    """
    Encodes MongoDB ObjectID.
    """

    def default(self, obj, **kwargs):
        if isinstance(obj, bson.objectid.ObjectId):
            return str(obj)
        else:
            return super(MongoEncoder, self).default(obj, **kwargs)


class Statistics:
    """
    The cache for statistics information.
    """

    _TTL = 3600.0

    _values = dict()
    _getters = dict()

    def __init__(self, db):
        self._db = db
        self._logger = logging.getLogger(Statistics.__name__)
        self._getters.update({
            "ssid_count": lambda: self._distinct_count("ssid"),
            "bssid_count": lambda: self._distinct_count("bssid"),
        })

    @property
    def ssid_count(self):
        return self._get_value("ssid_count")

    @property
    def bssid_count(self):
        return self._get_value("bssid_count")

    def _get_value(self, key):
        """
        Gets the statistics value.
        """

        # Get the getter.
        getter = self._getters.get(key)
        if not getter:
            self._logger.error("Unknown key: %s.", key)
            return None
        # Check for cached value.
        value, now = self._values.get(key), time.time()
        if (value is None) or (value[1] - now > self._TTL):
            # No cached value or it is outdated.
            self._logger.debug("Get %s.", key)
            self._values[key] = value = (getter(), now)
        else:
            self._logger.debug("Cached: %sms ago.", value[1] - now)
        # Return the value.
        self._logger.debug("Got %s: %s.", key, value)
        return value[0]

    def _distinct_count(self, field_name):
        """
        Get the distinct count of values of the specified field.
        """

        response = self._db.scan_results.aggregate([
            {"$group": {"_id": "$" + field_name}},
            {"$group": {"_id": None, "count": {"$sum": 1}}},
        ])
        if response["ok"]:
            return response["result"][0]["count"]
        else:
            return None
