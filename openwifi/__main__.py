#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Runs Open WiFi Server.
"""


import argparse
import logging
import sys

import openwifi.helpers.exit_codes

try:
    import openwifi.application
except ImportError as ex:
    print(str(ex), file=sys.stderr)
    sys.exit(openwifi.helpers.exit_codes.EX_SOFTWARE)


parser = argparse.ArgumentParser(
    prog="python3 -m openwifi",
    description=globals()["__doc__"],
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    "--log-path",
    default=sys.stderr,
    dest="log_file",
    help="log file path",
    metavar="LOG_PATH",
    type=argparse.FileType(mode="w+t"),
)
parser.add_argument(
    "--port",
    default=8080,
    dest="http_port",
    help="application HTTP port",
    metavar="PORT",
    type=int,
)
parser.add_argument(
    "--https-port",
    default=8443,
    dest="https_port",
    help="application HTTPS port",
    metavar="PORT",
    type=int,
)
parser.add_argument(
    "--log-level",
    choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    default=logging.INFO,
    dest="log_level",
    help="logging level",
)


try:
    args = parser.parse_args()
    # Configure logging.
    logging.basicConfig(
        format="%(asctime)s [%(process)d] %(name)s %(levelname)s: %(message)s",
        level=getattr(logging, args.log_level),
        stream=args.log_file,
    )
    # Run the main function.
    sys.exit(
        openwifi.application.Application().main(parser.parse_args()) or
        openwifi.helpers.exit_codes.EX_OK
    )
except Exception as ex:
    print(type(ex), file=sys.stderr)
    sys.exit(openwifi.helpers.exit_codes.EX_USAGE)