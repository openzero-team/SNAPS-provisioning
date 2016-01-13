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


def save_keys_to_files(keys=None, pub_file_path=None, priv_file_path=None):
    """
    Saves the generated RSA generated keys to the filesystem
    :param keys: the keys to save
    :param pub_file_path: the path to the public keys
    :param pub_file_path: the path to the private keys
    :return: None
    """
    if keys:
        if pub_file_path:
            public_handle = open(pub_file_path, 'wb')
            public_handle.write(keys.publickey().exportKey('OpenSSH'))
            public_handle.close()

        if priv_file_path:
            private_handle = open(priv_file_path, 'wb')
            private_handle.write(keys.exportKey())
            private_handle.close()


def upload_keypair_file(nova, name, file_path):
    """
    Uploads a public key from a file
    :param nova: the Nova client
    :param name: the keypair name
    :param file_path: the path to the public key file
    :return: the keypair object
    """
    with open(os.path.expanduser(file_path)) as fpubkey:
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
