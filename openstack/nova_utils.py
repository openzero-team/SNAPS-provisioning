import os
import logging
import novaclient.v2.client as novaclient

logger = logging.getLogger('nova_utils')

"""
Utilities for basic OpenStack Nova API calls
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


def upload_keypair_file(nova, name, filePath):
    """
    Uploads a public key from a file
    :param nova: the Nova client
    :param name: the keypair name
    :param filePath: the path to the public key file
    :return: the keypair object
    """
    with open(os.path.expanduser(filePath)) as fpubkey:
        return upload_keypair(nova, name, fpubkey.read())


def upload_keypair(nova, name, key):
    """
    Uploads a public key from a file
    :param nova: the Nova client
    :param name: the keypair name
    :param key: the public key object
    :return: the keypair object
    """
    return nova.keypairs.create(name=name, public_key=key)


def keypair_exists(nova, keypair_obj):
    """
    Returns a copy of the keypair object if found
    :param nova: the Nova client
    :param keypair_obj: the keypair object
    :return: the keypair object or None if not found
    """
    try:
        return nova.keypairs.get(keypair_obj)
    except:
        return None


def get_keypairs(nova):
    """
    Returns a list of all available keypairs
    :param nova: the Nova client
    :return: the list of objects
    """
    return nova.keypairs.list()


def delete_keypair(nova, key):
    """
    Deletes a keypair object from OpenStack
    :param nova: the Nova client
    :param key: the keypair object to delete
    """
    nova.keypairs.delete(key)
