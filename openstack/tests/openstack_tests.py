from openstack import create_network

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


def get_network_config():
    return OSNetworkConfig('test-priv-net', 'test-priv-subnet', '10.0.1.0/24', 'test-router')


class OSImageSettings:
    """
    Represents the settings required for creating an image in OpenStack
    """
    def __init__(self, img_format, url, name, download_file_path):
        self.format = img_format
        self.url = url
        self.name = name
        self.download_file_path = download_file_path


class OSNetworkConfig:
    """
    Represents the settings required for the creation of a network in OpenStack
    """
    def __init__(self, net_name, subnet_name, subnet_cidr, router_name):
        self.net_name = net_name
        self.network_settings = create_network.NetworkSettings(name=self.net_name)
        self.subnet_name = subnet_name
        self.subnet_cidr = subnet_cidr
        self.router_name = router_name
        self.router_settings = create_network.RouterSettings(name=self.router_name)
        self.subnet_settings = create_network.SubnetSettings(cidr=subnet_cidr, name=subnet_name)
