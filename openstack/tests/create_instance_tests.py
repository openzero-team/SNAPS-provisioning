import logging
import unittest
import time
from openstack import create_image
import openstack.create_instance as create_instance
import openstack.create_network as create_network
import openstack.neutron_utils as neutron_utils
from openstack import os_credentials

VM_BOOT_TIMEOUT = 180

# Initialize Logging
logging.basicConfig(level=logging.DEBUG)

# TODO - Find means to make this configurable
# From packstack Lab 1
# Change http_proxy to localhost:3128
os_auth_url = 'http://10.197.103.22:5000/v2.0/'
password = 'cable123'

username = 'admin'
tenant_name = 'admin'
os_creds = os_credentials.OSCreds(username, password, os_auth_url, tenant_name)

flavor = 'm1.tiny'
image_format = 'qcow2'
image_url = 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img'
image_name = 't1'
download_path = '/tmp/create_image_tests'
priv_net_name = 'test-priv-net'
priv_subnet_name = 'test-priv-subnet'
priv_subnet_cidr = '10.0.1.0/24'
router_name = 'test-router'
router_settings = create_network.RouterSettings(name=router_name)
port_name = 'test-port'
ip_1 = '10.0.1.100'
ip_2 = '10.0.1.200'
vm_inst_name = 'test-openstack-vm-instance-1'


class CreateInstanceTests(unittest.TestCase):
    """
    Test for the CreateImage class defined in create_image.py
    """

    def setUp(self):
        """
        Instantiates the CreateImage object that is responsible for downloading and creating an OS image file
        within OpenStack
        """
        # Create Image
        self.image_creator = create_image.OpenStackImage(os_creds, image_format, image_url, image_name, download_path)
        try:
            self.image_creator.create()
        except:
            self.image_creator.clean()

        # Create Network
        self.network_creator = create_network.OpenStackNetwork(os_creds,
                                                               create_network.NetworkSettings(name=priv_net_name),
                                                               create_network.SubnetSettings(cidr=priv_subnet_cidr,
                                                                                             name=priv_subnet_name),
                                                               router_settings)
        try:
            self.network_creator.create()
        except:
            self.network_creator.clean()
            self.image_creator.clean()

        port_settings = create_network.PortSettings(name=port_name, ip_address=ip_1)
        try:
            self.port = neutron_utils.create_port(self.network_creator.neutron, port_settings,
                                                  self.network_creator.network)
        except:
            neutron_utils.delete_port(self.network_creator.neutron, port_settings)
            self.network_creator.clean()
            # Removed for now as create instance sometimes intermittently works but the creator
            # will not attempt to upload a new image when one with the same name already exists
            # self.image_creator.clean()

        self.inst_creator = create_instance.OpenStackVmInstance(os_creds, vm_inst_name, flavor,
                                                                self.image_creator.image, [self.port])

    def tearDown(self):
        """
        Cleans the image and downloaded image file
        """
        if self.inst_creator:
            self.inst_creator.clean()
        if self.port:
            neutron_utils.delete_port(self.network_creator.neutron, self.port)
        if self.network_creator:
            self.network_creator.clean()
        if self.image_creator:
            self.image_creator.clean()

    def test_create_instance(self):
        """
        Tests the creation of an OpenStack network.
        """
        # Create Image
        vm_inst = self.inst_creator.create()

        self.assertTrue(vm_active(self.inst_creator.nova, vm_inst))
        self.assertEquals(vm_inst, self.inst_creator.vm)
        print vm_inst


def vm_active(nova, vm):
    """
    Returns true when the VM status returns 'ACTIVE' prior to the VM_BOOT_TIMEOUT value
    :param nova: The nova client
    :param vm: The VM instance
    :return: T/F
    """

    # sleep and wait for VM status change
    sleep_time = 3
    count = VM_BOOT_TIMEOUT / sleep_time
    while count > 0:
        count -= 1
        instance = nova.servers.get(vm.id)
        if instance.status == "ACTIVE":
            return True
        if instance.status == "ERROR" or count == 0:
            return False
        time.sleep(sleep_time)
    return False
