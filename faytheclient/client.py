# Copyright (c) 2020 kiennt2609@gmail.com.
# All Rights Reserved.

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import json
import logging
import time

import requests

from faytheclient import http

LOG = logging.getLogger(__name__)


class Client(http.HTTPClient):
    """Client for the Faythe API.

    :param endpoint: A user-supplied endpoint URL for the Faythe service.
    :param username: A username to generate jwt.
    :param password: A Faythe password to generate jwt.
    """

    jwt_expired_at = None

    def __init__(self, endpoint, username, password, **kwargs):
        """Initialize a new client for the Faythe API."""
        super(Client, self).__init__(endpoint, **kwargs)
        self.username = username
        self.password = password

        self.get_jwt_token()
        self.jwt_expired_at = time.time() + 60 * 40  # 40 minutes

    def get_jwt_token(self):
        try:
            # Get and store token in requests Session's cookie
            self.get('/public/login',
                     auth=(self.username, self.password))
            LOG.debug("Logged into Faythe %s" % self.endpoint)
        except Exception as e:
            LOG.exception("Unable to authenticate a user: {}".format(e))
            raise e

    class decorator(object):
        @staticmethod
        def refresh_jwt_token(decorated_func):
            def wrapper(api, *args, **kwargs):
                if time.time() > api.jwt_expired_at:
                    api.get_jwt_token()
                return decorated_func(api, *args, **kwargs)

            return wrapper

    @decorator.refresh_jwt_token
    def list_clouds(self):
        return self.get('/clouds')

    @decorator.refresh_jwt_token
    def register_cloud(self, provider, body):
        return self.post('/clouds/{}'. format(provider), data=body)

    @decorator.refresh_jwt_token
    def unregister_cloud(self, id):
        return self.delete('/clouds/{}'. format(id))

    @decorator.refresh_jwt_token
    def update_cloud(self, id, body=None):
        return self.put('/clouds/{}' . format(id), data=body)

    @decorator.refresh_jwt_token
    def create_scaler(self, cloud_id, body):
        return self.post('/scalers/{}' . format(cloud_id), data=body)

    @decorator.refresh_jwt_token
    def list_scalers(self, cloud_id):
        return self.get('/scalers/{}'. format(cloud_id))

    @decorator.refresh_jwt_token
    def delete_scaler(self, cloud_id):
        return self.delete('/scalers/{}' . format(cloud_id))

    @decorator.refresh_jwt_token
    def update_scaler(self, cloud_id, body=None):
        return self.put('/scalers/{}' . format(cloud_id), data=body)

    @decorator.refresh_jwt_token
    def list_nresolvers(self):
        return self.get('/nsresolvers')

    @decorator.refresh_jwt_token
    def list_healers(self, cloud_id):
        return self.get('/healers')

    @decorator.refresh_jwt_token
    def create_healer(self, cloud_id, body):
        return self.post('/healers/{}' . format(cloud_id), data=body)

    @decorator.refresh_jwt_token
    def delete_healers(self, cloud_id):
        return self.delete('/healers/{}' . format(cloud_id))

    @decorator.refresh_jwt_token
    def create_silence(self, cloud_id, body):
        return self.post('/silences/{}' . format(cloud_id),  data=body)

    @decorator.refresh_jwt_token
    def list_silences(self, cloud_id):
        return self.get('/silences/{}' . format(cloud_id))

    @decorator.refresh_jwt_token
    def delete_silence(self, cloud_id):
        return self.delete('/silences/{}' . format(cloud_id))
