from openstack import os_credentials

# TODO - deal with proxy settings here too

os_auth_url = 'http://10.197.103.22:5000/v2.0/'
password = 'cable123'

username = 'admin'
tenant_name = 'admin'


def get_credentials():
    # TODO - Find means to make this configurable
    # From packstack Lab 1
    # Change http_proxy to localhost:3128
    return os_credentials.OSCreds(username, password, os_auth_url, tenant_name)


def get_image_settings():
    return OSImageSettings('qcow2', 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img',
                           'test-image', '/tmp/create_image_tests')


class OSImageSettings:
    """
    Represents the settings required for creating an image in OpenStack
    """
    def __init__(self, format, url, name, download_file_path):
        self.format = format
        self.url = url
        self.name = name
        self.download_file_path = download_file_path
