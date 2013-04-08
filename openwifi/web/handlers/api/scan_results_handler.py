#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import calendar
import datetime
import http.client
import json
import logging
import re

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

    def get(self, timestamp=None, limit=None, *args, **kwargs):
        if not timestamp or not limit:
            self._logger.warning("Both timestamp and limit are required.")
            self.send_error(http.client.BAD_REQUEST)
            return

        # Check parameters.
        timestamp = int(timestamp)
        limit = int(limit)
        if timestamp < 0 or limit < 0:
            self._logger.warning("Invalid timestamp and limit: %s.", (timestamp, limit))
            self.send_error(http.client.BAD_REQUEST)
            return
        # Perform query.
        cursor = self._db.scan_results.find({
            "ts": {"$gt": timestamp},
        }, {
            "_id": False,
            "cid": False,
        }).limit(max(limit, 128))
        # Write response.
        scan_results = list(cursor)
        self._logger.debug("Got %s result(s).", len(scan_results))
        self.write(json.dumps(scan_results))

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
            if not isinstance(scan_result, dict) or not self._post(scan_result):
                self.send_error(status_code=http.client.BAD_REQUEST)
                return

        self.write(self._OK_RESPONSE)

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
                return False
            scan_result_document[key] = value

        self._db.scan_results.save(scan_result_document)
        self._logger.debug("Saved scan result: %s", scan_result_document)
        return True
