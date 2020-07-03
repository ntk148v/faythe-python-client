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
    headers = None

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
            resp = self.post('/tokens',
                             auth=(self.username, self.password))
            self.headers = {"Authorization": resp.headers['Authorization']}
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
        return self.get(url, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def register_cloud(self, provider, body):
        """Register a new cloud to Faythe

        :param provider: The cloud provider type. 'OpenStack' is the only
                         provider supported by now.
        :param body: A dictionary object.
        """
        url = utils.generate_url('/clouds', provider)
        return self.post(url, body=body, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def unregister_cloud(self, id):
        """Remove a cloud from Faythe

        :param id: The id of cloud.
        """
        url = utils.generate_url('/clouds', id)
        return self.delete(url. format(id), headers=self.headers).json()

    @decorator.refresh_jwt_token
    def update_cloud(self, id, body=None):
        """Update a cloud information

        :param id: The id of cloud.
        :param body: (optional) A dictionary object. If it
                     is None, the cloud won't be updated.
        """
        url = utils.generate_url('/clouds', id)
        return self.put(url, body=body, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def create_scaler(self, cloud_id, body):
        """Create a scaler belong to a cloud.

        :param cloud_id: The id of cloud.
        :param body: A dictionary object.
        """
        url = utils.generate_url('/scalers', cloud_id)
        return self.post(url, body=body, headers=self.headers).json()

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
        return self.get(url, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def delete_scaler(self, cloud_id):
        """Delete a scaler."""
        url = utils.generate_url('/scalers', cloud_id)
        return self.delete(url, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def update_scaler(self, cloud_id, body=None):
        """Update a scaler information.

        :param cloud_id: The id of cloud.
        :param body: (optional) A dictionary object. If it
                     is None, the scaler won't be updated.
        """
        url = utils.generate_url('/scalers', cloud_id)
        return self.put(url, body=body, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def list_nresolvers(self):
        """List all nresovlers (name resolvers)."""
        return self.get('/nsresolvers', headers=self.headers).json()

    @decorator.refresh_jwt_token
    def list_healers(self, cloud_id):
        """List all healers belong to a cloud.

        :param cloud_id: The id of cloud.
        """
        return self.get('/healers', headers=self.headers).json()

    @decorator.refresh_jwt_token
    def create_healer(self, cloud_id, body):
        """Create a new healer belongs to a cloud.

        :param cloud_id: The id of cloud.
        :param body: A dictionary object.
        """
        url = utils.generate_url('/healers', cloud_id)
        return self.post(url, body=body, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def delete_healers(self, cloud_id):
        """Delete a healer.

        :param cloud_id: The id of cloud.
        """
        url = utils.generate_url('/healers', cloud_id)
        return self.delete(url . format(cloud_id), headers=self.headers).json()

    @decorator.refresh_jwt_token
    def create_silence(self, cloud_id, body):
        """Create a silencer to ignore healing action.

        :param cloud_id: The id of cloud.
        :param body: A dictionary object.
        """
        url = utils.generate_url('/silences', cloud_id)
        return self.post(url,  body=body, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def list_silences(self, cloud_id):
        """List all silencers belong to a cloud.

        :param cloud_id: The id of cloud.
        """
        url = utils.generate_url('/silences', cloud_id)
        return self.get(url, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def delete_silence(self, cloud_id):
        """Delete a healer belong to a cloud.

        :param cloud_id: The id of cloud.
        """
        url = utils.generate_url('/silences', cloud_id)
        return self.delete(url, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def list_users(self):
        """List all Faythe users with policies."""
        url = utils.generate_url('/users')
        return self.get(url, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def create_user(self, user):
        """Create new Faythe user.

        :param user: A dict of user information.
                     for example: {'username': 'new', 'password': 'secret'}
        """
        url = utils.generate_url('/users')
        return self.post(url, headers=self.headers, data=user).json()

    @decorator.refresh_jwt_token
    def delete_user(self, username):
        """Delete an existing user.

        :param username: The name of user.
        """
        url = utils.generate_url('/users', username)
        return self.delete(url, headers=self.headers).json()

    @decorator.refresh_jwt_token
    def change_password(self, username, newpassword):
        """Change user's password.

        :param username: The name of user.
        :param newpassword: The new password.
        """
        url = utils.generate_url('/users', username, 'change_password')
        return self.put(url, headers=self.headers,
                        data={'newpassword': newpassword})

    @decorator.refresh_jwt_token
    def add_policies(self, username, body):
        """Add a set of policies.

        :param username: The name of user.
        :param body: A list of dictionary object.
        """
        url = utils.generate_url('/policies', username)
        return self.post(url, headers=self.headers, body=body).json()

    @decorator.refresh_jwt_token
    def remove_policies(self, username, body):
        """Remove a set of policies.

        :param username: The name of user.
        :param body: A list of dictionary object.
        """
        url = utils.generate_url('/policies', username)
        return self.delete(url, headers=self.headers, body=body).json()
