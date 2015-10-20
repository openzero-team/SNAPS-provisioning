import logging
from glanceclient import Client
from keystoneclient.auth.identity import v2 as identity
from keystoneclient import session
import keystoneclient.v2_0.client as ksclient

logger = logging.getLogger('glance_utils')

"""
Utilities for basic neutron API calls
"""


def glance_client(username, password, os_auth_url, tenant_name):
    """
    Creates and returns a glance client object
    :return: the glance client
    """
    logger.info('Retrieving Keystone Client')
    keystone = ksclient.Client(**{
        'username': username,
        'password': password,
        'auth_url': os_auth_url,
        'tenant_name': tenant_name})
    glance_endpoint = keystone.service_catalog.url_for(service_type='image', endpoint_type='publicURL')
    auth = identity.Password(auth_url=os_auth_url, username=username, password=password,
                             tenant_name=tenant_name)
    sess = session.Session(auth=auth)
    token = auth.get_token(sess)

    logger.info('Retrieving Glance Client')
    return Client('2', endpoint=glance_endpoint, token=token)
