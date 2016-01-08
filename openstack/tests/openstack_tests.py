from openstack import os_credentials

# TODO - deal with proxy settings here too

def get_credentials():
    # TODO - Find means to make this configurable
    # From packstack Lab 1
    # Change http_proxy to localhost:3128
    os_auth_url = 'http://10.197.103.22:5000/v2.0/'
    password = 'cable123'

    username = 'admin'
    tenant_name = 'admin'
    return os_credentials.OSCreds(username, password, os_auth_url, tenant_name)