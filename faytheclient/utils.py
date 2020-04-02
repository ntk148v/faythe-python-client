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


def generate_url(url, *args, **kwargs):
    """Generate an url with input arguments.

    *args -> path parameter.
    *kwargs -> query parameter.
    """
    url = url.rstrip('/')
    if args:
        url = '/'.join([url, *args])
    if kwargs:
        for k, v in kwargs.items():
            if k == list(kwargs.keys())[0]:
                url += "?{}={}" . format(k, v)
                continue
            url += "&{}={}" . format(k, v)
    return url
