# Copyright (c) 2016 Cable Television Laboratories, Inc. ("CableLabs")
#                    and others.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
__author__ = 'spisarski'

import logging
from glanceclient import Client
from keystoneclient.auth.identity import v2 as identity
from keystoneclient import session
import keystoneclient.v2_0.client as ksclient

logger = logging.getLogger('glance_utils')

"""
Utilities for basic neutron API calls
"""


def glance_client(os_creds):
    """
    Creates and returns a glance client object
    :return: the glance client
    """
    logger.info('Retrieving Keystone Client')
    keystone = ksclient.Client(**{
        'username': os_creds.username,
        'password': os_creds.password,
        'auth_url': os_creds.auth_url,
        'tenant_name': os_creds.tenant_name})
    glance_endpoint = keystone.service_catalog.url_for(service_type='image', endpoint_type='publicURL')
    auth = identity.Password(auth_url=os_creds.auth_url, username=os_creds.username, password=os_creds.password,
                             tenant_name=os_creds.tenant_name)
    sess = session.Session(auth=auth)
    token = auth.get_token(sess)

    logger.info('Retrieving Glance Client')
    return Client('2', endpoint=glance_endpoint, token=token)
