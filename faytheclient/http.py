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

import copy
import json
import logging
import socket

import requests
import simplejson

from faytheclient import exceptions

USER_AGENT = 'faytheclient'
LOG = logging.getLogger(__name__)


class HTTPClient(object):
    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint.strip('/')
        if not endpoint.startswith('http') and not endpoint.startswith('https'):
            self.endpoint = 'http://{}'.format(endpoint)
        self.timeout = float(kwargs.get('timeout', 600))
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

    def __del__(self):
        if self.session:
            try:
                self.session.close()
            except Exception as e:
                LOG.exception(e)
            finally:
                self.session = None

    def _request(self, method, url, body=None, **kwargs):
        """Send an http request with the specified characteristics.
        """
        # Copy the kwargs so we can reuse the original in case of redirects
        headers = copy.deepcopy(kwargs.pop('headers', {}))
        if headers.get('Content-Type', 'application/json') is None:
            headers['Content-Type'] = 'application/json'
        if self.endpoint.endswith("/") or url.startswith("/"):
            conn_url = "%s%s" % (self.endpoint, url)
        else:
            conn_url = "%s/%s" % (self.endpoint, url)
        try:
            resp = self.session.request(method, conn_url,
                                        json=body, headers=headers,
                                        timeout=self.timeout, **kwargs)
        except requests.exceptions.Timeout as e:
            message = ("Error communicating with %(url)s: %(e)s" %
                       dict(url=conn_url, e=e))
            raise exceptions.InvalidEndpoint(message=message)
        except requests.exceptions.ConnectionError as e:
            message = ("Error finding address for %(url)s: %(e)s" %
                       dict(url=conn_url, e=e))
            raise exceptions.CommunicationError(message=message)
        except socket.gaierror as e:
            message = "Error finding address for %s: %s" % (
                self.endpoint, e)
            raise exceptions.InvalidEndpoint(message=message)
        except (socket.error, socket.timeout, IOError) as e:
            endpoint = self.endpoint
            message = ("Error communicating with %(endpoint)s %(e)s" %
                       {'endpoint': endpoint, 'e': e})
            raise exceptions.CommunicationError(message=message)
        except Exception as e:
            raise e

        LOG.debug('%(method)s call to image for %(url)s.',
                  {'method': resp.request.method,
                   'url': resp.url})
        return self._handle_response(resp)

    def _handle_response(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            err_msg = str(e)

            # Attempt to get Error message from response
            try:
                error_dict = response.json()
            except (json.decoder.JSONDecodeError,
                    simplejson.errors.JSONDecodeError):
                pass
            else:
                err_msg += " [Error: {}]".format(error_dict)
            raise requests.exceptions.HTTPError(err_msg)
        else:
            return response

    def head(self, url, **kwargs):
        return self._request('HEAD', url, **kwargs)

    def get(self, url, **kwargs):
        return self._request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self._request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self._request('PUT', url, **kwargs)

    def patch(self, url, **kwargs):
        return self._request('PATCH', url, **kwargs)

    def delete(self, url, **kwargs):
        return self._request('DELETE', url, **kwargs)
