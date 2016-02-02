import logging
import time
import unittest
import os

from ansible.runner import Runner
from ansible.inventory import Inventory

from openstack import create_image
import openstack.create_instance as create_instance
import openstack.create_network as create_network
import openstack.neutron_utils as neutron_utils
import openstack.nova_utils as nova_utils
import openstack.create_keypairs as create_keypairs
import openstack_tests

VM_BOOT_TIMEOUT = 600

# Initialize Logging
logging.basicConfig(level=logging.DEBUG)

os_creds = openstack_tests.get_credentials()
priv_net_config = openstack_tests.get_priv_net_config()
pub_net_config = openstack_tests.get_pub_net_config()

flavor = 'm1.medium'

ip_1 = '10.0.1.100'
ip_2 = '10.0.1.200'
vm_inst_name = 'test-openstack-vm-instance-1'
keypair_name = 'testKP'
keypair_pub_filepath = '/tmp/testKP.pub'
keypair_priv_filepath = '/tmp/testKP'


class CreateInstanceSingleNetworkTests(unittest.TestCase):
    """
    Test for the CreateInstance class with a single NIC/Port
    """

    def setUp(self):
        """
        Instantiates the CreateImage object that is responsible for downloading and creating an OS image file
        within OpenStack
        """
        # Create Image
        os_image_settings = openstack_tests.get_image_test_settings()
        self.image_creator = create_image.OpenStackImage(os_creds, os_image_settings.format, os_image_settings.url,
                                                         os_image_settings.name, os_image_settings.download_file_path)
        self.image_creator.create()

        # Create Network
        self.network_creator = create_network.OpenStackNetwork(os_creds, pub_net_config.network_settings,
                                                               pub_net_config.subnet_settings,
                                                               pub_net_config.router_settings)
        self.network_creator.create()

        self.keypair_creator = create_keypairs.OpenStackKeypair(os_creds,
                                            create_keypairs.KeypairSettings(name=keypair_name,
                                                                            public_filepath=keypair_pub_filepath,
                                                                            private_filepath=keypair_priv_filepath))
        self.keypair_creator.create()

        self.ports = list()
        self.inst_creator = None

    def tearDown(self):
        """
        Cleans the created object
        """
        if self.inst_creator:
            self.inst_creator.clean()

        if self.keypair_creator:
            self.keypair_creator.clean()

        if os.path.isfile(keypair_pub_filepath):
            os.remove(keypair_pub_filepath)

        if os.path.isfile(keypair_priv_filepath):
            os.remove(keypair_priv_filepath)

        for port in self.ports:
            neutron_utils.delete_port(self.network_creator.neutron, port)

        if self.network_creator:
            self.network_creator.clean()

        # This is a big image file so we probably do not want to remove from OS after each test
        if self.image_creator:
            self.image_creator.clean()

    def test_single_port_dhcp(self):
        """
        Tests the creation of an OpenStack instance with a single port with a DHCP assigned IP.
        """
        port_settings = create_network.PortSettings(name='test-port-1')
        self.ports.append(neutron_utils.create_port(self.network_creator.neutron, port_settings,
                                                    self.network_creator.network))
        self.inst_creator = create_instance.OpenStackVmInstance(os_creds, vm_inst_name, flavor,
                                                                self.image_creator.image, self.ports)
        vm_inst = self.inst_creator.create()

        self.assertTrue(vm_active(self.inst_creator.nova, vm_inst))
        self.assertEquals(vm_inst, self.inst_creator.vm)

    def test_single_port_static(self):
        """
        Tests the creation of an OpenStack instance with a single port with a static IP.
        """
        port_settings = create_network.PortSettings(name='test-port-1', ip_address=ip_1)
        self.ports.append(neutron_utils.create_port(self.network_creator.neutron, port_settings,
                                                    self.network_creator.network))
        floating_ip_conf = {'port_name': 'test-port-1', 'ext_net': pub_net_config.router_settings.external_gateway}
        self.inst_creator = create_instance.OpenStackVmInstance(os_creds, vm_inst_name, flavor,
                                                                self.image_creator.image, self.ports,
                                                                floating_ip_conf=floating_ip_conf)
        vm_inst = self.inst_creator.create()

        self.assertEquals(ip_1, self.inst_creator.ports[0]['port']['dns_assignment'][0]['ip_address'])
        self.assertTrue(vm_active(self.inst_creator.nova, vm_inst))
        self.assertEquals(vm_inst, self.inst_creator.vm)


class CreateInstancePubPrivNetTests(unittest.TestCase):
    """
    Test for the CreateInstance class with two NIC/Ports, eth0 with floating IP and eth1 w/o
    """

    def setUp(self):
        """
        Instantiates the CreateImage object that is responsible for downloading and creating an OS image file
        within OpenStack
        """
        # Create Image
        self.os_image_settings = openstack_tests.get_instance_image_settings()
        self.image_creator = create_image.OpenStackImage(os_creds, self.os_image_settings.format,
                                                         self.os_image_settings.url,
                                                         self.os_image_settings.name,
                                                         self.os_image_settings.download_file_path)
        self.image_creator.create()

        # Create Network
        self.network_creators = list()
        # First network is public
        self.network_creators.append(create_network.OpenStackNetwork(os_creds, pub_net_config.network_settings,
                                                                     pub_net_config.subnet_settings,
                                                                     pub_net_config.router_settings))
        # Second network is private
        self.network_creators.append(create_network.OpenStackNetwork(os_creds, priv_net_config.network_settings,
                                                                     priv_net_config.subnet_settings,
                                                                     priv_net_config.router_settings))
        for network_creator in self.network_creators:
            network_creator.create()

        self.keypair_creator = create_keypairs.OpenStackKeypair(os_creds,
                                                create_keypairs.KeypairSettings(name=keypair_name,
                                                                                public_filepath=keypair_pub_filepath,
                                                                                private_filepath=keypair_priv_filepath))
        self.keypair_creator.create()

        self.ports = list()
        self.inst_creator = None

    def tearDown(self):
        """
        Cleans the created objects
        """
        if self.inst_creator:
            self.inst_creator.clean()

        if self.keypair_creator:
            self.keypair_creator.clean()

        if os.path.isfile(keypair_pub_filepath):
            os.remove(keypair_pub_filepath)

        if os.path.isfile(keypair_priv_filepath):
            os.remove(keypair_priv_filepath)

        for port in self.ports:
            neutron_utils.delete_port(self.network_creators[0].neutron, port)

        for network_creator in self.network_creators:
            network_creator.clean()

    def test_dual_ports_dhcp(self):
        """
        Tests the creation of an OpenStack instance with a dual ports/NICs with a DHCP assigned IP.
        NOTE: This test and any others that call ansible will most likely fail unless you do one of
        two things:
        1. Have a ~/.ansible.cfg (or alternate means) to set host_key_checking = False
        2. Set the following environment variable in your executing shell: ANSIBLE_HOST_KEY_CHECKING=False
        Should this not be performed, the creation of the host ssh key will cause your ansible calls to fail.
        """
        floating_ip_conf = dict()
        # Create ports/NICs for instance
        for network_creator in self.network_creators:
            idx = self.network_creators.index(network_creator)
            # port_name = 'test-port-' + `idx`
            port_name = 'test-port-' + repr(idx)
            if idx == 0:
                floating_ip_conf = {'port_name': port_name, 'ext_net': pub_net_config.router_settings.external_gateway}

            port_settings = create_network.PortSettings(name=port_name)
            self.ports.append(neutron_utils.create_port(network_creator.neutron, port_settings,
                                                        network_creator.network))

        # Create instance
        self.inst_creator = create_instance.OpenStackVmInstance(os_creds, vm_inst_name, flavor,
                                                                self.image_creator.image, self.ports,
                                                                keypair_name=self.keypair_creator.keypair_settings.name,
                                                                floating_ip_conf=floating_ip_conf)
        vm_inst = self.inst_creator.create()
        self.assertEquals(vm_inst, self.inst_creator.vm)

        # TODO - Move vm_active and vm_ping to create_instance and allow to block on create
        # Effectively blocks until VM has been properly activated
        self.assertTrue(vm_active(self.inst_creator.nova, vm_inst))

        floating_ip = nova_utils.get_floating_ip(self.inst_creator.nova, self.inst_creator.floating_ip)

        # Effectively blocks until VM's ssh port has been opened
        self.assertTrue(vm_ping(floating_ip.ip, self.os_image_settings.image_user,
                                self.keypair_creator.keypair_settings.private_filepath))


def vm_ping(ip, user, private_key_file, timeout=VM_BOOT_TIMEOUT):
    """
    Returns true when a ping is successfully executed prior to the timeout
    :param ip: The IP address to ping
    :param user: The user credentials to the machine attempting to ping
    :param private_key_file: The file path to the private key
    :param timeout: Returns false if ping does not occur prior to this timeout value
    :return: T/F
    """
    runner = Runner(module_name='ping', inventory=Inventory(host_list=[ip]), pattern='all', remote_user=user,
                    private_key_file=private_key_file)

    # sleep and wait for VM status change
    sleep_time = 3
    count = timeout / sleep_time
    while count > 0:
        result = runner.run()
        count -= 1
        if result.get('contacted'):
            return True
        # if result['dark'][ip]['failed'] or count < 1:
        #     return False
        time.sleep(sleep_time)
    return False


def vm_active(nova, vm, timeout=VM_BOOT_TIMEOUT):
    """
    Returns true when the VM status returns 'ACTIVE' prior to the VM_BOOT_TIMEOUT value
    :param nova: The nova client
    :param vm: The VM instance
    :return: T/F
    """
    # sleep and wait for VM status change
    sleep_time = 3
    count = timeout / sleep_time
    while count > 0:
        count -= 1
        instance = nova.servers.get(vm.id)
        if instance.status == "ACTIVE":
            return True
        if instance.status == "ERROR" or count < 1:
            return False
        time.sleep(sleep_time)
    return False
