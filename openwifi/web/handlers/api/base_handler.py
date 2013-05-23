#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import http.client
import logging

import requests

import openwifi.web.handlers.base_handler


class BaseHandler(openwifi.web.handlers.base_handler.BaseHandler):
    """
    Base request handler for API.
    """

    _CONTENT_TYPE_HEADER = "Content-Type"
    _X_CLIENT_ID_HEADER = "X-Client-ID"
    _X_AUTH_TOKEN_HEADER = "X-Auth-Token"

    def initialize(self, cache):
        super(BaseHandler, self).initialize()

        self._logger = logging.getLogger(BaseHandler.__name__)

        assert cache is not None
        self._cache = cache

    def prepare(self):
        super(BaseHandler, self).prepare()

        # Obtain the client ID.
        self._client_id = self.request.headers.get(self._X_CLIENT_ID_HEADER)
        self._logger.debug("%s: %s", self._X_CLIENT_ID_HEADER, self._client_id)
        # Obtain the authentication token. 
        auth_token = self.request.headers.get(self._X_AUTH_TOKEN_HEADER)
        self._logger.debug("%s: %s", self._X_AUTH_TOKEN_HEADER, auth_token)
        # Authenticate the user.
        self._user_id = self._authenticate(auth_token)
        self._logger.debug("User ID: %s", self._user_id)

        self.set_header("Content-Type", "application/json")

    def _authenticate(self, auth_token):
        """
        Authenticates the user.
        """

        # Validate the authentication token format.
        if not auth_token:
            return None
        # Redis key. Do not store authentication tokens "as is".
        key = "auth:" + self._hash(auth_token)
        # Check if the token is in the cache.
        user_id = self._cache.get(key)
        if user_id:
            # Explicitly convert from bytes to string.
            return str(user_id, "ascii")
        # Verify the token.
        self._logger.debug("Verifiying the token %s", auth_token)
        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/tokeninfo",
            params={"access_token": auth_token},
        )
        if response.status_code != requests.codes.ok:
            return None
        # The token is valid. Obtain the user ID.
        token_info = response.json()
        # Depersonalize the user. 
        user_id = self._hash(token_info["user_id"])
        # Put the user ID into the cache.
        self._cache.set(key, user_id , ex=token_info["expires_in"])
        # And return the user ID.
        return user_id

    def _hash(self, data):
        return hashlib.sha1(data).hexdigest()
