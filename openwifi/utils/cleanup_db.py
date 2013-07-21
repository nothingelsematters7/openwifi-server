#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleanup DB service utility.
"""

import logging
import operator
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
        # Initialize statistics.
        total_scan_result_count = 0
        max_scan_results_per_bssid = 0
        total_old_scan_result_count = 0
        # Iterate over the aggregated results.
        self._logger.info("Iterating over the aggregated results ...")
        for scan_results in aggregated_scan_results:
            # Unpack result.
            bssid, scan_results = scan_results["_id"], scan_results["scan_results"]
            # Update statistics.
            total_scan_result_count += len(scan_results)
            max_scan_results_per_bssid = max(max_scan_results_per_bssid, len(scan_results))
            # Sort the results by timestamp and skip ten of them.
            sorted_scan_results = sorted(scan_results, key=operator.itemgetter("ts"), reverse=True)
            old_scan_results = sorted_scan_results[10:]
            if not old_scan_results:
                # No old results.
                continue
            # Remove old results by _id.
            self._logger.debug("[%s]: %s old results.", bssid, len(old_scan_results))
            self._logger.debug(
                "Most recent at %s, old start at %s.",
                sorted_scan_results[0]["ts"],
                old_scan_results[0]["ts"],
            )
            for old_scan_result in old_scan_results:
                # Move the result.
                self._logger.debug("Moving %s ...", old_scan_result["_id"])
                old_scan_result = db.scan_results.find_one(old_scan_result["_id"])
                if old_scan_result is not None:
                    db.scan_results.remove(old_scan_result["_id"])
                    db.old_scan_results.insert(old_scan_result)
            # Update statistics.
            total_old_scan_result_count += len(old_scan_results)
        # Finished.
        self._logger.info("Done.")
        self._logger.info("Total %s old scan results.", total_old_scan_result_count)
        self._logger.info(
            "Was %.1f results per BSSID (%s max).",
            total_scan_result_count / len(aggregated_scan_results),
            max_scan_results_per_bssid,
        )
        self._logger.info("Finished.")
        return openwifi.helpers.exit_codes.EX_OK
