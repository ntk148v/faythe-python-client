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
from faytheclient import utils

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
        """Get and store jwt in its Session's cookies"""
        try:
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
    def list_clouds(self, **kwargs):
        """List all clouds that are registerd to Faythe

        :param provider: (optional) Filter a cloud result by provider.
                         The only supported provider is OpenStack so
                         this one is useless right now.
        :param id: (optional) Filter cloud result by id.
        :param tags: (optional) A list of tags to filter the cloud list by.
                     Clouds that match all tags in this list will be returned.
        :param tags_any: (optional) A list of tags to filter the cloud list by.
                         Clouds that match any tags in this list will be returned.
        """
        url = utils.generate_url('/clouds', **kwargs)
        return self.get(url)

    @decorator.refresh_jwt_token
    def register_cloud(self, provider, body):
        """Register a new cloud to Faythe

        :param provider: The cloud provider type. 'OpenStack' is the only
                         provider supported by now.
        :param body: A dictionary object.
        """
        url = utils.generate_url('/clouds', provider)
        return self.post(url, body=body)

    @decorator.refresh_jwt_token
    def unregister_cloud(self, id):
        """Remove a cloud from Faythe

        :param id: The id of cloud.
        """
        url = utils.generate_url('/clouds', id)
        return self.delete(url. format(id))

    @decorator.refresh_jwt_token
    def update_cloud(self, id, body=None):
        """Update a cloud information

        :param id: The id of cloud.
        :param body: (optional) A dictionary object. If it
                     is None, the cloud won't be updated.
        """
        url = utils.generate_url('/clouds', id)
        return self.put(url, body=body)

    @decorator.refresh_jwt_token
    def create_scaler(self, cloud_id, body):
        """Create a scaler belong to a cloud.

        :param cloud_id: The id of cloud.
        :param body: A dictionary object.
        """
        url = utils.generate_url('/scalers', cloud_id)
        return self.post(url, body=body)

    @decorator.refresh_jwt_token
    def list_scalers(self, cloud_id, **kwargs):
        """List all scalers belong to a cloud.

        :param cloud_id: The id of cloud.
        :param tags: (optional) A list of tags to filter the scaler list by.
                     Scalers that match all tags in this list will be returned.
        :param tags_any: (optional) A list of tags to filter the scaler list by.
                         Scalers that match any tags in this list will be returned.
        """
        url = utils.generate_url('/scalers', cloud_id, **kwargs)
        return self.get(url)

    @decorator.refresh_jwt_token
    def delete_scaler(self, cloud_id):
        """Delete a scaler."""
        url = utils.generate_url('/scalers', cloud_id)
        return self.delete(url)

    @decorator.refresh_jwt_token
    def update_scaler(self, cloud_id, body=None):
        """Update a scaler information.

        :param cloud_id: The id of cloud.
        :param body: (optional) A dictionary object. If it
                     is None, the scaler won't be updated.
        """
        url = utils.generate_url('/scalers', cloud_id)
        return self.put(url, body=body)

    @decorator.refresh_jwt_token
    def list_nresolvers(self):
        """List all nresovlers (name resolvers)."""
        return self.get('/nsresolvers')

    @decorator.refresh_jwt_token
    def list_healers(self, cloud_id):
        """List all healers belong to a cloud.

        :param cloud_id: The id of cloud.
        """
        return self.get('/healers')

    @decorator.refresh_jwt_token
    def create_healer(self, cloud_id, body):
        """Create a new healer belongs to a cloud.

        :param cloud_id: The id of cloud.
        :param body: A dictionary object.
        """
        url = utils.generate_url('/healers', cloud_id)
        return self.post(url, body=body)

    @decorator.refresh_jwt_token
    def delete_healers(self, cloud_id):
        """Delete a healer.

        :param cloud_id: The id of cloud.
        """
        url = utils.generate_url('/healers', cloud_id)
        return self.delete(url . format(cloud_id))

    @decorator.refresh_jwt_token
    def create_silence(self, cloud_id, body):
        """Create a silencer to ignore healing action.

        :param cloud_id: The id of cloud.
        :param body: A dictionary object.
        """
        url = utils.generate_url('/silences', cloud_id)
        return self.post(url,  body=body)

    @decorator.refresh_jwt_token
    def list_silences(self, cloud_id):
        """List all silencers belong to a cloud.

        :param cloud_id: The id of cloud.
        """
        url = utils.generate_url('/silences', cloud_id)
        return self.get(url)

    @decorator.refresh_jwt_token
    def delete_silence(self, cloud_id):
        """Delete a healer belong to a cloud.

        :param cloud_id: The id of cloud.
        """
        url = utils.generate_url('/silences', cloud_id)
        return self.delete(url)
