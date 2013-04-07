#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


_validators = {
    "bssid": _validate_bssid,
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
            if not isinstance(scan_result, dict) or not self._post(scan_result):
                self.send_error(status_code=http.client.BAD_REQUEST)
                return

        self._logger.debug("Got scan result: %s", scan_result)

        self.write(self._OK_RESPONSE)

    def _post(self, scan_result):
        """
        Posts the scan result.
        """

        scan_result_document = dict()

        for key, value in scan_result.items():
            validate = _validators.get(key)
            if not validate:
                continue
            if not validate(value):
                return False
            scan_result_document[key] = value

        self._db.scan_results.save(scan_result_document)
        return True
