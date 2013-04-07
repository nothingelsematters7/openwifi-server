#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Makes the Open WiFi server tarball.
"""

import argparse
import compileall
import logging
import os
import sys
import tarfile

import openwifi


def main(args):
    global with_sources
    with_sources = args.with_sources

    logging.info("Compiling into byte-code ...")
    compileall.compile_dir(
        dir=os.path.dirname(openwifi.__file__),
        optimize=2,
    )

    logging.info("Compressing ...")
    with tarfile.open(mode="w:gz", fileobj=args.output) as tarball:
        tarball.add(
            os.path.abspath(os.path.dirname(openwifi.__file__)),
            filter=_filter,
        )
        tarball.add(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "requirements.txt")),
            filter=_filter,
        )


def _create_argument_parser():
    parser = argparse.ArgumentParser(
        prog="python3 make-tarball.py",
        description=globals()["__doc__"],
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="output file",
        type=argparse.FileType("wb"),
        required=True,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        dest="verbose",
        help="verbose mode",
    )
    parser.add_argument(
        "--with-sources",
        action="store_true",
        default=False,
        dest="with_sources",
        help="add *.py to the archive also",
    )

    return parser


def _filter(tar_info):
    # Cut path prefix.
    root_path = os.path.abspath(os.path.dirname(__file__))
    tar_info.name = tar_info.name[len(root_path):]

    if tar_info.isdir():
        logging.info("Adding directory %s", tar_info.name)
        return tar_info

    _, extension = os.path.splitext(tar_info.name)
    if extension.lower() in (
        ".pyc",
        ".pyo",
        ".pyc",
        ".css",
        ".ico",
        ".png",
        ".mustache",
        ".csv",
        ".pem",
        ".txt",
    ) or (
        extension.lower() == ".py" and with_sources
    ):
        logging.info("Adding file %s", tar_info.name)
        return tar_info
    else:
        logging.debug("Skipped %s", tar_info.name)
        return None


if __name__ == "__main__":
    args = _create_argument_parser().parse_args()
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO if not args.verbose else logging.DEBUG,
        stream=sys.stderr,
    )
    sys.exit(main(args) or 0)