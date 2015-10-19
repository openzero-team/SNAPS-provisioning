import unittest
import time
from openstack import create_image
import openstack.create_instance as create_instance
import openstack.create_network as create_network
import openstack.neutron_utils as neutron_utils

VM_BOOT_TIMEOUT = 180

# This is currently pointing to the CL OPNFV Lab 2 environment and these tests will break should there not be network
# connectivity to this location.
os_auth_url = 'http://10.197.123.37:5000/v2.0'

username = 'admin'
password = 'octopus'
tenant_name = 'admin'
flavor = 'm1.small'
image_format = 'qcow2'
image_url = 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img'
image_name = 'test-image'
download_path = '/tmp/create_image_tests'
priv_net_name = 'test-priv-net'
priv_subnet_name = 'test-priv-subnet'
priv_subnet_cidr = '10.197.122.0/24'
router_name = 'test-router'
port_name = 'test-port'
ip_1 = '10.197.122.10'
ip_2 = '10.197.122.20'
vm_inst_name = 'test-openstack-vm-instance-1'


class CreateNetworkSuccessTests(unittest.TestCase):
    """
    Test for the CreateImage class defined in create_image.py
    """

    def setUp(self):
        """
        Instantiates the CreateImage object that is responsible for downloading and creating an OS image file
        within OpenStack
        """
        # Create Image
        self.image_creator = create_image.OpenStackImage(username, password, os_auth_url, tenant_name, image_format,
                                                         image_url, image_name, download_path)
        self.image_creator.create()

        # Create Network
        self.network_creator = create_network.OpenStackNetwork(username, password, os_auth_url, tenant_name,
                                                               priv_net_name, priv_subnet_name, priv_subnet_cidr,
                                                               router_name)
        self.network_creator.create()

        self.port = neutron_utils.create_port(self.network_creator.neutron, port_name, self.network_creator.network,
                                              ip_1)

        self.inst_creator = create_instance.OpenStackVmInstance(username, password, os_auth_url, tenant_name,
                                                                vm_inst_name, flavor, self.image_creator.image,
                                                                self.port)

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
