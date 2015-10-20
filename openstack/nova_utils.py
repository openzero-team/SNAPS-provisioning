import logging
import novaclient.v2.client as novaclient

logger = logging.getLogger('nova_utils')

"""
Utilities for basic neutron API calls
"""


def nova_client(username, password, os_auth_url, tenant_name):
    """
    Instantiates and returns a client for communications with OpenStack's Nova server
    :param username: the username for connecting to the OpenStack remote API
    :param password: the password for connecting to the OpenStack remote API
    :param os_auth_url: the endpoint for connecting to the OpenStack remote API
    :param tenant_name: the tenant name for connecting to the OpenStack remote API
    :return: the client object
    """
    logger.info('Retrieving Nova Client')
    return novaclient.Client(**{
        'username': username,
        'api_key': password,
        'auth_url': os_auth_url,
        'project_id': tenant_name,
    })
