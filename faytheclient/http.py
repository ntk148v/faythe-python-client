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

import logging

import requests

USER_AGENT = 'faythe-python-client'
LOG = logging.getLogger(__name__)


class HTTPClient(object):
    def __init__(self, endpoint, username, password, **kwargs):
        self.endpoint = endpoint.strip('/')
        if not endpoint.startswith('http') and not endpoint.startswith('https'):
            self.endpoint = 'http://{}'.format(endpoint)
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

        if self.endpoint.startswith("https"):

            if kwargs.get('insecure', False) is True:
                self.session.verify = False
            else:
                if kwargs.get('cacert', None) is not '':
                    self.session.verify = kwargs.get('cacert', True)

            self.session.cert = (kwargs.get('cert_file'),
                                    kwargs.get('key_file'))
