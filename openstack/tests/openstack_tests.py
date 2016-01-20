import os

from openstack import create_network
from openstack import os_credentials
import file_utils

username = 'admin'
tenant_name = 'admin'


def get_credentials():
    config = file_utils.read_yaml('conf/os_env.yaml')
    if config.get('http_proxy'):
        os.environ['HTTP_PROXY'] = config['http_proxy']
    return os_credentials.OSCreds(config['username'], config['password'], config['os_auth_url'], config['tenant_name'])


def get_image_settings():
    return OSImageSettings('qcow2', 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img',
                           'test-image', '/tmp/create_image_tests')


def get_network_config():
    return OSNetworkConfig('test-priv-net', 'test-priv-subnet', '10.0.1.0/24', 'test-router',
                           external_gateway='external')


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
    def __init__(self, net_name, subnet_name, subnet_cidr, router_name, external_gateway=None):
        self.net_name = net_name
        self.network_settings = create_network.NetworkSettings(name=self.net_name)
        self.subnet_name = subnet_name
        self.subnet_cidr = subnet_cidr
        self.router_name = router_name
        self.router_settings = create_network.RouterSettings(name=self.router_name, external_gateway=external_gateway)
        self.subnet_settings = create_network.SubnetSettings(cidr=subnet_cidr, name=subnet_name)
