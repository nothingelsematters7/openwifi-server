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
import pymongo
import pymongo.errors

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

    return isinstance(value, str) and len(value) <= 32


def _validate_timestamp(value):
    """
    Validates timestamp.
    """

    return (
        isinstance(value, int) and
        # value is stored in ms.
        value / 1000 < calendar.timegm(datetime.datetime.utcnow().utctimetuple())
    )


def _validate_accuracy(value):
    """
    Validate accuracy.
    """

    return (isinstance(value, int) and 0 <= value) or (isinstance(value, float) and 0.0 <= value)


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


def _filter_scan_result(scan_result):
    # Do not accept to large accuracy.
    return scan_result["acc"] <= 100.0


class ScanResultsHandler(openwifi.web.handlers.api.base_handler.BaseHandler):
    """
    Scan results request handler.
    """

    # Prevents the entire collection to be loaded into memory at once.
    _GET_SCAN_RESULTS_LIMIT = 128

    # noinspection PyMethodOverriding
    def initialize(self, db, cache):
        super(ScanResultsHandler, self).initialize(cache)

        self._db = db
        self._logger = logging.getLogger(ScanResultsHandler.__name__)

    def get(self, last_id=None, limit=None, *args, **kwargs):
        try:
            # Check headers.
            if not self._client_id:
                raise ValueError("No client ID.")
            # Parse parameters.
            limit = int(limit)
            if limit < 0:
                raise ValueError("Invalid limit: %s" % limit)
            last_id = bson.objectid.ObjectId(last_id)
        except (ValueError, bson.objectid.InvalidId) as ex:
            self._logger.warning("Value error: %s", ex)
            self.send_error(http.client.BAD_REQUEST)
            return
        # Perform query.
        cursor = self._db.scan_results.find({
            "_id": {"$gt": last_id},
            "cid": {"$ne": self._client_id},
        }, {
            "cid": False,
            "uid": False,
        }).sort([("_id", pymongo.ASCENDING)]).limit(min(limit, self._GET_SCAN_RESULTS_LIMIT))
        # Write response.
        scan_results = list(cursor)
        self._logger.debug("Got %s result(s).", len(scan_results))
        self.write(json.dumps(scan_results, cls=openwifi.helpers.MongoEncoder))

    def post(self, *args, **kwargs):
        # Initialize with None as it will be used in except block.
        scan_results = None
        try:
            # Check the headers.
            if not self._client_id:
                raise ValueError("No client ID.")
            if not self._user_id:
                raise ValueError("No user ID.")
            # Deserialize the scan results.
            scan_results = self.request.body.decode("utf-8")
            scan_results = json.loads(scan_results)
            if not isinstance(scan_results, list):
                raise ValueError("Scan result is not a list.")
            self._logger.debug("Got %s scan results.", len(scan_results))
            for scan_result in scan_results:
                # Validate the document.
                if len(scan_result) != len(_validators):
                    raise ValueError("Invalid document size.")
                for key, value in scan_result.items():
                    validate = _validators.get(key)
                    # Check the value.
                    if not validate or not validate(value):
                        raise ValueError("Validation failed: %s" % repr((key, value)))
                if not scan_result["ssid"]:
                    self._logger.warning("Skipped empty SSID: [cid=%s].", self._client_id)
                    continue
                # Check the document value.
                if _filter_scan_result(scan_result):
                    # Attach the client ID and the user ID.
                    scan_result.update({
                        "cid": self._client_id,
                        "uid": self._user_id,
                    })
                    # Insert the document.
                    try:
                        self._db.scan_results.insert(
                            scan_result,
                            # Generate _id on the client side.
                            manipulate=True,
                        )
                    except pymongo.errors.DuplicateKeyError:
                        # Perhaps, the (cid, ts, bssid) index was violated.
                        self._logger.debug("Duplicate: %s", scan_result)
                    else:
                        self._logger.debug("Saved scan result: %s", scan_result)
        except ValueError as ex:
            self._logger.warning("Value error: %s from client %s on %s", ex, self._client_id, scan_results)
            self.send_error(status_code=http.client.BAD_REQUEST)
            return
