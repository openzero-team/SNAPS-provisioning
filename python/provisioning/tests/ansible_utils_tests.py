# Copyright (c) 2016 Cable Television Laboratories, Inc. ("CableLabs")
#                    and others.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

import openstack.create_instance as create_instance
import openstack.create_keypairs as create_keypairs
import openstack.create_network as create_network
import openstack.neutron_utils as neutron_utils
from openstack import create_image
from scp import SCPClient

from provisioning import ansible_utils
from openstack.tests import openstack_tests
from openstack.tests.os_source_file_test import OSSourceFileTestsCase

VM_BOOT_TIMEOUT = 600

# Initialize Logging
logging.basicConfig(level=logging.DEBUG)

priv_net_config = openstack_tests.get_priv_net_config()
pub_net_config = openstack_tests.get_pub_net_config()

flavor = 'm1.medium'

ip_1 = '10.0.1.100'
ip_2 = '10.0.1.200'
vm_inst_name = 'test-openstack-vm-instance-1'
keypair_name = 'testKP'
keypair_pub_filepath = 'tmp/testKP.pub'
keypair_priv_filepath = 'tmp/testKP'


class AnsibleProvisioningTests(OSSourceFileTestsCase):
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
        self.image_creator = create_image.OpenStackImage(self.os_creds, self.os_image_settings.image_user,
                                                         self.os_image_settings.format,
                                                         self.os_image_settings.url,
                                                         self.os_image_settings.name,
                                                         self.os_image_settings.download_file_path)
        self.image_creator.create()

        # Create Network
        self.network_creators = list()
        # First network is public
        self.network_creators.append(create_network.OpenStackNetwork(self.os_creds, pub_net_config.network_settings,
                                                                     pub_net_config.subnet_settings,
                                                                     pub_net_config.router_settings))
        # Second network is private
        self.network_creators.append(create_network.OpenStackNetwork(self.os_creds, priv_net_config.network_settings,
                                                                     priv_net_config.subnet_settings,
                                                                     priv_net_config.router_settings))
        for network_creator in self.network_creators:
            network_creator.create()

        self.keypair_creator = create_keypairs.OpenStackKeypair(self.os_creds,
                                                                create_keypairs.KeypairSettings(name=keypair_name,
                                                                                public_filepath=keypair_pub_filepath,
                                                                                private_filepath=keypair_priv_filepath))
        self.keypair_creator.create()

        floating_ip_conf = dict()

        ports = []
        for network_creator in self.network_creators:
            idx = self.network_creators.index(network_creator)
            # port_name = 'test-port-' + `idx`
            port_name = 'test-port-' + repr(idx)
            if idx == 0:
                floating_ip_conf = {'port_name': port_name, 'ext_net': pub_net_config.router_settings.external_gateway}

            port_settings = create_network.PortSettings(name=port_name)
            ports.append(neutron_utils.create_port(network_creator.neutron, port_settings, network_creator.network))

        # Create instance
        self.inst_creator = create_instance.OpenStackVmInstance(self.os_creds, vm_inst_name, flavor,
                                                                self.image_creator, ports,
                                                                self.os_image_settings.image_user,
                                                                keypair_creator=self.keypair_creator,
                                                                floating_ip_conf=floating_ip_conf)
        self.inst_creator.create()

        self.test_file_local_path = '/tmp/hello.txt'

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

        for network_creator in self.network_creators:
            network_creator.clean()

        if os.path.isfile(self.test_file_local_path):
            os.remove(self.test_file_local_path)

    def test_apply_simple_playbook(self):
        """
        Tests application of an Ansible playbook that simply copies over a file:
        1. Have a ~/.ansible.cfg (or alternate means) to set host_key_checking = False
        2. Set the following environment variable in your executing shell: ANSIBLE_HOST_KEY_CHECKING=False
        Should this not be performed, the creation of the host ssh key will cause your ansible calls to fail.
        """
        # Block until VM's ssh port has been opened
        self.inst_creator.config_rpm_nics()
        self.assertTrue(self.inst_creator.vm_ssh_active(block=True))

        priv_key = self.inst_creator.keypair_creator.keypair_settings.private_filepath
        ip = self.inst_creator.floating_ip.ip
        user = self.inst_creator.remote_user
        retval = ansible_utils.apply_playbook('provisioning/tests/playbooks/simple_playbook.yml', [ip], user, priv_key)
        self.assertEquals(0, retval)

        ssh = ansible_utils.ssh_client(ip, user, priv_key, self.os_creds.proxy)
        self.assertIsNotNone(ssh)
        scp = SCPClient(ssh.get_transport())
        scp.get('~/hello.txt', self.test_file_local_path)

        self.assertTrue(os.path.isfile(self.test_file_local_path))

        with open(self.test_file_local_path) as f:
            file_contents = f.readline()
            self.assertEquals('Hello World!', file_contents)

    def test_apply_template_playbook(self):
        """
        Tests application of an Ansible playbook that applies a template to a file:
        1. Have a ~/.ansible.cfg (or alternate means) to set host_key_checking = False
        2. Set the following environment variable in your executing shell: ANSIBLE_HOST_KEY_CHECKING=False
        Should this not be performed, the creation of the host ssh key will cause your ansible calls to fail.
        """
        # Block until VM's ssh port has been opened
        self.inst_creator.config_rpm_nics()
        self.assertTrue(self.inst_creator.vm_ssh_active(block=True))

        priv_key = self.inst_creator.keypair_creator.keypair_settings.private_filepath
        ip = self.inst_creator.floating_ip.ip
        user = self.inst_creator.remote_user
        ansible_utils.apply_playbook('provisioning/tests/playbooks/template_playbook.yml', [ip], user, priv_key,
                                     variables={'name': 'Foo'})

        ssh = ansible_utils.ssh_client(ip, user, priv_key, self.os_creds.proxy)
        self.assertIsNotNone(ssh)
        scp = SCPClient(ssh.get_transport())
        scp.get('/tmp/hello.txt', self.test_file_local_path)

        self.assertTrue(os.path.isfile(self.test_file_local_path))

        with open(self.test_file_local_path) as f:
            file_contents = f.readline()
            self.assertEquals('Hello Foo!', file_contents)
