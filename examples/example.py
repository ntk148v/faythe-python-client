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

import os
import json
import hashlib

from faytheclient import client

if __name__ == '__main__':
    try:
        endpoint = os.environ['FAYTHE_ENDPOINT']
        username = os.environ['FAYTHE_USERNAME']
        password = os.environ['FAYTHE_PASSWORD']
    except KeyError as e:
        print('Missing environment variables! %s' % str(e))
        raise e
    fcli = client.Client(endpoint, username, password)
    # Openstack auth_url
    auth_url = "http://192.169.1.2:5000/v3"
    encoded_auth_url = auth_url.encode()
    cloud_id = hashlib.md5(encoded_auth_url).hexdigest()
    # Create a cloud
    create_cloud_body = {
        "auth": {
            "username": "admin",
            "auth_url": auth_url,
            "password": "fakepassword",
            "project_name": "admin",
            "domain_name": "Default",
            "region_name": "RegionOne"
        },
        "monitor": {
            "backend": "prometheus",
            "address": "http://192.169.1.3:9091/",
            "username": "admin",
            "password": "fakepassword"
        },
        "atengine": {
            "backend": "stackstorm",
            "address": "http://192.169.1.4",
            "apikey": "fakepassword"
        },
        "provider": "openstack",
        "tags": [
            "test",
        ]
    }
    print(fcli.register_cloud('openstack', create_cloud_body))
    # List all clouds
    print(fcli.list_clouds())
    # List a single cloud
    print(fcli.list_clouds(id=cloud_id))
    # Create scalers
    create_scaler_body = {
        "query": "asg:memory:avg{stack_asg_name=\"cloud-portal-autoscaling\"} > 75",
        "duration": "5m",
        "interval": "60s",
        "actions": {
            "scale_out": {
                "url": "http://192.169.1.2:8000/v1/signal/fakeactionurl",
                "attempts": 4,
                "delay": "50ms",
                "type": "http",
                "delay_type": "backoff",
                "method": "POST"
            }
        },
        "cooldown": "10m",
        "metadata": {
            "group": "cloud_portal"
        },
        "active": True
    }
    print(fcli.create_scaler(cloud_id, create_scaler_body))
    # List all scalers
    print(fcli.list_scalers(cloud_id))
    # Create a user
    print(fcli.create_user({'username': 'newuser', 'password': 'newpassword'}))
    # List all users
    print(fcli.list_users())
