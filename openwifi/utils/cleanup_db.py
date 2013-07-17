#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleanup DB service utility.
"""

import logging
import time

import bson.son

import openwifi.helpers.exit_codes


class CleanupDB:
    """
    Cleanup DB utility main class.
    """

    def __init__(self):
        self._logger = logging.getLogger(CleanupDB.__name__)

    def main(self, args, db):
        self._logger.info("Starting cleaning up the database ...")
        # Group scan results by BSSID.
        self._logger.debug("Running the aggregation query ...")
        aggregate_start_time = time.time()
        aggregation_result = db.scan_results.aggregate([
            {"$sort": bson.son.SON(_id=1)},
            {"$group": {
                "_id": "$bssid",
                "scan_results": {"$push": {"_id": "$_id", "ts": "$ts"}},
            }},
        ])
        aggregate_end_time = time.time()
        if not aggregation_result.get("ok"):
            self._logger.fatal("Aggregation query has failed: %s", aggregation_result)
            return openwifi.helpers.exit_codes.EX_SOFTWARE
        aggregated_scan_results = aggregation_result["result"]
        self._logger.info(
            "Got %s aggregated scan results in %.3fs.",
            len(aggregated_scan_results),
            aggregate_end_time - aggregate_start_time,
        )
        # Iterate over the aggregated results.
        self._logger.info("Iterating over the aggregated results ...")
        total_scan_result_count = 0
        max_scan_results_per_bssid = 0
        for scan_results in aggregated_scan_results:
            total_scan_result_count += len(scan_results["scan_results"])
            max_scan_results_per_bssid = max(max_scan_results_per_bssid, len(scan_results["scan_results"]))
            # Sort the results by timestamp.
            # Remove old results by _id.
        # Finished.
        self._logger.info("Done.")
        self._logger.info(
            "Was %.1f results per BSSID (%s max).",
            total_scan_result_count / len(aggregated_scan_results),
            max_scan_results_per_bssid,
        )
        self._logger.info("Finished.")
        return openwifi.helpers.exit_codes.EX_OK
