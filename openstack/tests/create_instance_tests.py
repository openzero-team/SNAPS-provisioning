import logging
import time
from openstack import create_image
import unittest
import openstack.create_instance as create_instance
import openstack.create_network as create_network
import openstack.neutron_utils as neutron_utils
import openstack_tests

VM_BOOT_TIMEOUT = 180

# Initialize Logging
logging.basicConfig(level=logging.DEBUG)

os_creds = openstack_tests.get_credentials()
os_image_settings = openstack_tests.get_image_settings()
priv_net_config = openstack_tests.get_network_config()

flavor = 'm1.tiny'

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
        self.image_creator = create_image.OpenStackImage(os_creds, os_image_settings.format, os_image_settings.url,
                                                         os_image_settings.name, os_image_settings.download_file_path)
        try:
            self.image_creator.create()
        except Exception:
            self.image_creator.clean()

        # Create Network
        self.network_creator = create_network.OpenStackNetwork(os_creds, priv_net_config.network_settings,
                                                               priv_net_config.subnet_settings,
                                                               priv_net_config.router_settings)
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
