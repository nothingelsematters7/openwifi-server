#!/usr/env/bin python3
# -*- coding: utf-8 -*-

"""
Contains used exit codes.
"""

import os


_os_dict = os.__dict__


EX_OK = _os_dict.get("EX_OK", 0)
EX_USAGE = _os_dict.get("EX_USAGE", 1)