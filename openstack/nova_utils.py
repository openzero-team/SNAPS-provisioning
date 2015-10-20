import logging
import novaclient.v2.client as novaclient

logger = logging.getLogger('nova_utils')

"""
Utilities for basic neutron API calls
"""


def nova_client(os_creds):
    """
    Instantiates and returns a client for communications with OpenStack's Nova server
    :param os_creds: The connection credentials to the OpenStack API
    :return: the client object
    """
    logger.info('Retrieving Nova Client')
    return novaclient.Client(**{
        'username': os_creds.username,
        'api_key': os_creds.password,
        'auth_url': os_creds.auth_url,
        'project_id': os_creds.tenant_name,
    })
