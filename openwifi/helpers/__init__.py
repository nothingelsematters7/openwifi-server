#!/usr/env/bin python3
# -*- coding: utf-8 -*-

"""
Helper classes and functions.
"""

import json

# noinspection PyPackageRequirements
import bson.objectid


class MongoEncoder(json.JSONEncoder):
    """
    Encodes MongoDB ObjectID.
    """

    def default(self, obj, **kwargs):
        if isinstance(obj, bson.objectid.ObjectId):
            return str(obj)
        else:
            return super(MongoEncoder, self).default(obj, **kwargs)