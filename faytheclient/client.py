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

LOG = logging.getLogger(__name__)


class Client(object):
    """Client for the Faythe API.

    :param endpoint: A user-supplied endpoint URL for the Faythe service.
    :param username: A username to generate jwt.
    :param password: A Faythe password to generate jwt.
    """

    jwt = None
    jwt_expired_at = None
    headers = None

    def __init__(self, endpoint, username, password):
        """Initialize a new client for the Faythe API."""
        self.endpoint = endpoint.strip('/')
        if not endpoint.startswith('http') and not endpoint.startswith('https'):
            self.endpoint = 'http://{}'.format(endpoint)
        self.username = username
        self.password = password

        self.get_jwt_token()
        self.jwt_expired_at = time.time() + 60 * 40  # 40 minutes

    def get_jwt_token(self):
        try:
            r = requests.post(
                self.endpoint + "/api/auth",
                data=json.dumps({"Username": self.username,
                                 "Password": self.password}))
            r.raise_for_status()
            jwt = r.json()
            self.jwt = jwt.get('jwt')
            self.headers = {"Authorization": "Bearer {}".format(self.jwt)}
            LOG.debug("Logged into Portainer %s" % self.endpoint)
        except Exception as e:
            LOG.exception("Unable to authenticate a user: {}".format(e))