"""
Utilities required for standard OpenStack library usage
"""


def get_credentials(username, password, os_auth_url, tenant_name):
    """
    Returns a creds dictionary object that is generally required of OpenStack API client instantiation
    :return: the credentials
    """
    return {
        'username': username,
        'password': password,
        'auth_url': os_auth_url,
        'tenant_name': tenant_name,
    }
