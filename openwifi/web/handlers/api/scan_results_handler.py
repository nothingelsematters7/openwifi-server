#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import calendar
import datetime
import http.client
import json
import logging
import re

# noinspection PyPackageRequirements
import bson.objectid

import openwifi.helpers
import openwifi.web.handlers.api.base_handler


_bssid_re = re.compile(r"([0-9a-f]{2}:){5}[0-9a-f]{2}")


def _validate_bssid(value):
    """
    Validates BSSID.
    """

    return isinstance(value, str) and bool(_bssid_re.match(value))


def _validate_ssid(value):
    """
    Validates SSID.
    """

    return isinstance(value, str) and len(value)


def _validate_timestamp(value):
    """
    Validates timestamp.
    """

    return (
        isinstance(value, int) and
        value < calendar.timegm(datetime.datetime.utcnow().utctimetuple())
    )


def _validate_accuracy(value):
    """
    Validate accuracy.
    """

    return isinstance(value, float) and 0.0 <= value <= 250.0


def _validate_location(value):
    # Check for the type.
    if not isinstance(value, dict):
        return False
    # Extract values.
    latitude, longitude = map(value.get, ("lat", "lon"))
    # Check latitude.
    if not isinstance(latitude, float) or latitude < -90.0 or latitude > +90.0:
        return False
    # Check longitude.
    if not isinstance(longitude, float) or longitude < -180.0 or longitude > +180.0:
        return False
    # All validations passed.
    return True


_validators = {
    "bssid": _validate_bssid,
    "ssid": _validate_ssid,
    "ts": _validate_timestamp,
    "acc": _validate_accuracy,
    "loc": _validate_location,
}


class ScanResultsHandler(openwifi.web.handlers.api.base_handler.BaseHandler):
    """
    Scan results request handler.
    """

    # noinspection PyMethodOverriding
    def initialize(self, db):
        super(ScanResultsHandler, self).initialize()

        self._db = db
        self._logger = logging.getLogger(ScanResultsHandler.__name__)

    def get(self, last_id=None, limit=None, *args, **kwargs):
        # Parse parameters.
        limit = int(limit)
        if limit < 0:
            self._logger.warning("Invalid limit: '%s'.", limit)
            self.send_error(http.client.BAD_REQUEST)
            return
        try:
            last_id = bson.objectid.ObjectId(last_id)
        except bson.objectid.InvalidId:
            self._logger.warning("Invalid last ID: '%s'.", last_id)
            self.send_error(http.client.BAD_REQUEST)
            return
        # Perform query.
        cursor = self._db.scan_results.find({
            "_id": {"$gt": last_id},
        }, {
            "cid": False,
        }).limit(max(limit, 128))
        # Write response.
        scan_results = list(cursor)
        self._logger.debug("Got %s result(s).", len(scan_results))
        self.write(json.dumps(scan_results, cls=openwifi.helpers.MongoEncoder))

    def post(self, *args, **kwargs):
        scan_result = None
        try:
            scan_result = self.request.body.decode("utf-8")
            scan_result = json.loads(scan_result)
        except ValueError:
            self._logger.warning("Value error.")
            self._logger.debug("Body: %s", scan_result)
            self.send_error(status_code=http.client.BAD_REQUEST)
            return
        else:
            self._logger.debug("Got scan result: %s", scan_result)
            _id = self._post(scan_result)
            if not isinstance(scan_result, dict) or _id is None:
                self.send_error(status_code=http.client.BAD_REQUEST)
                return

        self.write(json.dumps(_id, cls=openwifi.helpers.MongoEncoder))

    def _post(self, scan_result):
        """
        Posts the scan result.
        """

        scan_result_document = {
            "cid": self._client_id,
        }

        for key, value in scan_result.items():
            validate = _validators.get(key)
            if not validate:
                continue
            if not validate(value):
                self._logger.warning("Validation failed: %s", (key, value))
                return None
            scan_result_document[key] = value

        _id = self._db.scan_results.insert(scan_result_document, manipulate=True)
        self._logger.debug("Inserted scan result: %s", scan_result_document)
        return _id
