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

    return bool(_bssid_re.match(value))


def _validate_timestamp(value):
    """
    Validates timestamp.
    """

    return value < calendar.timegm(datetime.datetime.utcnow().utctimetuple())


_validators = {
    "bssid": _validate_bssid,
    "ssid": len,
    "ts": _validate_timestamp,
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

    def prepare(self):
        super(ScanResultsHandler, self).prepare()

        pass

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
