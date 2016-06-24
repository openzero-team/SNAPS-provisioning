#!/usr/bin/python
#
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
#
# This script is responsible for deploying a VM running virtual CMTS emulator instances
import logging
import os
import argparse
from provisioning import ansible_utils
import file_utils
from openstack import neutron_utils
from openstack import nova_utils
from openstack import os_credentials

__author__ = 'spisarski'

logger = logging.getLogger('deploy_vnfs')

ARG_NOT_SET = "argument not set"


def get_os_credentials(os_conn_config):
    """
    Returns an object containing all of the information required to access OpenStack APIs
    :param os_conn_config: The configuration holding the credentials
    :return: an OSCreds instance
    """
    return os_credentials.OSCreds(os_conn_config.get('username'),
                                  os_conn_config.get('password'),
                                  os_conn_config.get('auth_url'),
                                  os_conn_config.get('tenant_name'),
                                  os_conn_config.get('http_proxy'))


def create_image(os_conn_config, image_config):
    """
    Creates an image in OpenStack if necessary
    :param os_conn_config: The OS credentials from config
    :param image_config: The image configuration
    :return: A reference to the image creator object from which the image object can be accessed
    """
    from openstack.create_image import OpenStackImage
    image_creator = OpenStackImage(get_os_credentials(os_conn_config), image_config.get('image_user'),
                                   image_config.get('format'), image_config.get('download_url'),
                                   image_config.get('name'), image_config.get('local_download_path'))
    image_creator.create()
    return image_creator


def create_network(os_conn_config, network_config):
    """
    Creates a network on which the CMTSs can attach
    :param os_conn_config: The OpenStack credentials object
    :param network_config: The network configuration
    :return: A reference to the network creator objects for each network from which network elements such as the
             subnet, router, interface router, and network objects can be accessed.
    """
    # Check for OS for network existence
    # If exists return network instance data
    # Else, create network and return instance data
    from openstack.create_network import OpenStackNetwork
    from openstack.create_network import NetworkSettings
    from openstack.create_network import SubnetSettings
    from openstack.create_network import RouterSettings

    config = network_config['network']

    logger.info('Attempting to create network with name - ' + config.get('name'))

    # try:
    network_creator = OpenStackNetwork(get_os_credentials(os_conn_config),
                                       NetworkSettings(name=config.get('name')),
                                       SubnetSettings(config.get('subnet')),
                                       RouterSettings(config.get('router')))
    network_creator.create()
    logger.info('Created network ')
    return network_creator


def create_keypair(os_conn_config, keypair_config):
    """
    Creates a keypair that can be applied to an instance
    :param os_conn_config: The OpenStack credentials object
    :param keypair_config: The keypair configuration
    :return: A reference to the keypair creator object
    """
    from openstack.create_keypairs import OpenStackKeypair
    from openstack.create_keypairs import KeypairSettings

    keypair_creator = OpenStackKeypair(get_os_credentials(os_conn_config), KeypairSettings(keypair_config))
    keypair_creator.create()
    return keypair_creator


def create_vm_instance(os_conn_config, instance_config, image, network_dict, keypair_creator):
    """
    Creates a VM instance
    :param os_conn_config: The OpenStack credentials
    :param instance_config: The VM instance configuration
    :param image: The VM image
    :param network_dict: A dictionary of network objects returned by OpenStack where the key contains the network name.
    :param keypair_creator: The object responsible for creating the keypair associated with this VM instance.
    :return: A reference to the VM instance object
    """
    from openstack.create_network import PortSettings
    from openstack.create_instance import OpenStackVmInstance

    os_creds = get_os_credentials(os_conn_config)
    neutron = neutron_utils.neutron_client(os_creds)
    config = instance_config['instance']
    ports_config = config['ports']
    existing_ports = neutron.list_ports()['ports']
    ports = list()

    for port_config in ports_config:
        network_name = port_config['port']['network_name']
        port_name = port_config['port']['name']
        found = False
        for existing_port in existing_ports:
            if existing_port['name'] == port_name:
                existing_port_dict = {'port': existing_port}
                ports.append(existing_port_dict)
                found = True

        if not found:
            os_network_obj = network_dict.get(network_name)
            if os_network_obj:
                logger.info('Creating port [' + port_config['port']['name'] + '] for network name - ' + network_name)
                port_setting = PortSettings(port_config)
                ports.append(
                    neutron_utils.create_port(neutron, port_setting, os_network_obj.network, os_network_obj.subnet))
            else:
                logger.warn('Cannot create port as associated network name of [' + network_name + '] not configured.')
                raise Exception

    from openstack.create_image import OpenStackImage
    # TODO - need to configure in the image username
    image_creator = OpenStackImage(image=image, image_user='centos')
    vm_inst = OpenStackVmInstance(os_creds, config['name'], config['flavor'], image_creator, ports, config['sudo_user'],
                                  keypair_creator, config.get('floating_ip'))
    vm_inst.create()
    return vm_inst


def create_images(os_conn_config, images_config):
    """
    Returns a dictionary of images where the key is the image name and the value is the image object
    :param os_conn_config: The OpenStack connection credentials
    :param images_config: The list of image configurations
    :return: dictionary
    """
    if images_config:
        images = {}
        for image_config_dict in images_config:
            image_config = image_config_dict.get('image')
            if image_config and image_config.get('name'):
                images[image_config['name']] = create_image(os_conn_config, image_config)
        logger.info('Created configured images')
        return images
    return dict()


def create_networks(os_conn_config, network_confs):
    """
    Returns a dictionary of networks where the key is the network name and the value is the network object
    :param os_conn_config: The OpenStack connection credentials
    :param network_confs: The list of network configurations
    :return: dictionary
    """
    if network_confs:
        network_dict = {}
        if network_confs:
            for network_conf in network_confs:
                net_name = network_conf['network']['name']
                network_dict[net_name] = create_network(os_conn_config, network_conf)
        logger.info('Created configured networks')
        return network_dict
    return dict()


def create_keypairs(os_conn_config, keypair_confs):
    """
    Returns a dictionary of keypairs where the key is the keypair name and the value is the keypair object
    :param os_conn_config: The OpenStack connection credentials
    :param keypair_confs: The list of keypair configurations
    :return: dictionary
    """
    if keypair_confs:
        keypairs_dict = {}
        if keypair_confs:
            for keypair_dict in keypair_confs:
                keypair_config = keypair_dict['keypair']
                keypairs_dict[keypair_config['name']] = create_keypair(os_conn_config, keypair_config)
        logger.info('Created configured keypairs')
        return keypairs_dict
    return dict()


def create_instances(os_conn_config, instances_config, images, network_dict, keypairs_dict):
    """
    Returns a dictionary of instances where the key is the instance name and the value is the VM object
    :param os_conn_config: The OpenStack connection credentials
    :param instances_config: The list of VM instance configurations
    :param images: A dictionary of images that will probably be used to instantiate the VM instance
    :param network_dict: A dictionary of networks that will probably be used to instantiate the VM instance
    :param keypairs_dict: A dictionary of keypairs that will probably be used to instantiate the VM instance
    :return: dictionary
    """
    if instances_config:
        vm_dict = {}
        for instance_config in instances_config:
            instance = instance_config.get('instance')
            if instance:
                if images:
                    inst_image = images.get(instance.get('imageName')).image
                else:
                    nova = nova_utils.nova_client(os_credentials.OSCreds(os_conn_config.get('username'),
                                                                         os_conn_config.get('password'),
                                                                         os_conn_config.get('auth_url'),
                                                                         os_conn_config.get('tenant_name'),
                                                                         os_conn_config.get('http_proxy')))
                    inst_image = nova.images.find(name=instance.get('imageName'))
                if inst_image:
                    vm_dict[instance['name']] = create_vm_instance(os_conn_config, instance_config,
                                                                   inst_image, network_dict,
                                                                   keypairs_dict[instance['keypair_name']])

        logger.info('Created configured instances')
        return vm_dict
    return dict()


def __apply_ansible_playbooks(ansible_configs, vm_dict):
    """
    Applies ansible playbooks to running VMs with floating IPs
    :param ansible_configs: a list of Ansible configurations
    :param vm_dict: the dictionary of newly instantiated VMs where the VM name is the key
    :return: t/f - true if successful
    """
    logger.info("Applying Ansible Playbooks")
    if ansible_configs:
        # Ensure all hosts are accepting SSH session requests
        for vm_inst in vm_dict.values():
            if not vm_inst.vm_ssh_active(block=True):
                logger.warn("Timeout waiting for instance to respond to SSH requests")
                return False

        # Apply playbooks
        for ansible_config in ansible_configs:
            apply_ansible_playbook(ansible_config, vm_dict)

    return True


def apply_ansible_playbook(ansible_config, vm_dict):
    """
    Applies an Ansible configuration setting
    :param ansible_config: the configuration settings
    :param vm_dict: the dictionary of newly instantiated VMs where the VM name is the key
    :return:
    """
    if ansible_config:
        remote_user, floating_ips, private_key_filepath = __get_floating_ips(ansible_config, vm_dict)
        if floating_ips:
            ansible_utils.apply_playbook(ansible_config['playbook_location'], floating_ips, remote_user,
                                         private_key_filepath,
                                         variables=__get_variables(ansible_config.get('variables'), vm_dict))


def __get_floating_ips(ansible_config, vm_dict):
    """
    Returns a list of floating IP addresses
    :param ansible_config: the configuration settings
    :param vm_dict: the dictionary of VMs where the VM name is the key
    :return: tuple where the first element is the user and the second is a list of floating IPs and the third is the
    private key file location
    (note: in order to work, each of the hosts need to have the same sudo_user and private key file location values)
    """
    if ansible_config.get('hosts'):
        hosts = ansible_config['hosts']
        if len(hosts) > 0:
            floating_ips = list()
            remote_user = None
            private_key_filepath = None
            for host in hosts:
                vm = vm_dict.get(host)
                if vm:
                    remote_user = vm.remote_user
                    floating_ips.append(vm.floating_ip.ip)
                    private_key_filepath = vm.keypair_creator.keypair_settings.private_filepath
            return remote_user, floating_ips, private_key_filepath
    return None


def __get_variables(var_config, vm_dict):
    """
    Returns a dictionary of substitution variables to be used for Ansible templates
    :param var_config: the variable configuration settings
    :param vm_dict: the dictionary of VMs where the VM name is the key
    :return: dictionary or None
    """
    if var_config and vm_dict and len(vm_dict) > 0:
        variables = dict()
        for key, value in var_config.iteritems():
            value = __get_variable_value(value, vm_dict)
            variables[key] = value
            logger.info("Set Jinga2 variable with key [" + key + "] the value [" + value + ']')
        return variables
    return None


def __get_variable_value(var_config_values, vm_dict):
    """
    Returns the associated variable value for use by Ansible for substitution purposes
    :param var_config_values: the configuration dictionary
    :param vm_dict: the dictionary containing all VMs where the key is the VM's name
    :return:
    """
    if var_config_values['type'] == 'string':
        return __get_string_variable_value(var_config_values)
    if var_config_values['type'] == 'vm-attr':
        return __get_vm_attr_variable_value(var_config_values, vm_dict)
    if var_config_values['type'] == 'os_creds':
        return __get_os_creds_variable_value(var_config_values, vm_dict)
    if var_config_values['type'] == 'port':
        return __get_vm_port_variable_value(var_config_values, vm_dict)
    return None


def __get_string_variable_value(var_config_values):
    """
    Returns the associated string value
    :param var_config_values: the configuration dictionary
    :return: the value contained in the dictionary with the key 'value'
    """
    return var_config_values['value']


def __get_vm_attr_variable_value(var_config_values, vm_dict):
    """
    Returns the associated value contained on a VM instance
    :param var_config_values: the configuration dictionary
    :param vm_dict: the dictionary containing all VMs where the key is the VM's name
    :return: the value
    """
    vm = vm_dict.get(var_config_values['vm_name'])
    if vm:
        if var_config_values['value'] == 'floating_ip':
            return vm.floating_ip.ip


def __get_os_creds_variable_value(var_config_values, vm_dict):
    """
    Returns the associated OS credentials value
    :param var_config_values: the configuration dictionary
    :param vm_dict: the dictionary containing all VMs where the key is the VM's name
    :return: the value
    """
    logger.info("Retrieving OS Credentials")
    vm = vm_dict.values()[0]
    if var_config_values['value'] == 'username':
        logger.info("Returning OS username")
        return vm.os_creds.username
    elif var_config_values['value'] == 'password':
        logger.info("Returning OS password")
        return vm.os_creds.password
    elif var_config_values['value'] == 'auth_url':
        logger.info("Returning OS auth_url")
        return vm.os_creds.auth_url
    elif var_config_values['value'] == 'tenant_name':
        logger.info("Returning OS tenant_name")
        return vm.os_creds.tenant_name

    logger.info("Returning none")
    return None


def __get_vm_port_variable_value(var_config_values, vm_dict):
    """
    Returns the associated OS credentials value
    :param var_config_values: the configuration dictionary
    :param vm_dict: the dictionary containing all VMs where the key is the VM's name
    :return: the value
    """
    port_name = var_config_values.get('port_name')
    vm_name = var_config_values.get('vm_name')
    if port_name and vm_name:
        vm = vm_dict.get(vm_name)
        if vm:
            ports = vm.ports
            for port in ports:
                if port['port']['name'] == port_name:
                    port_value_id = var_config_values.get('port_value')
                    if port_value_id:
                        if port_value_id == 'mac_address':
                            return port['port']['mac_address']
                        if port_value_id == 'ip_address':
                            # Currently only supporting the first IP assigned to a given port
                            return port['port']['dns_assignment'][0]['ip_address']


def main(arguments):
    """
    Will need to set environment variable ANSIBLE_HOST_KEY_CHECKING=False or ...
    Create a file located in /etc/ansible/ansible/cfg or ~/.ansible.cfg containing the following content:

    [defaults]
    host_key_checking = False

    CWD must be this directory where this script is located.

    :return: To the OS
    """
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Starting to Deploy')
    config = file_utils.read_yaml(arguments.environment)
    logger.info('Read configuration file - ' + arguments.environment)

    if config:
        os_config = config.get('openstack')

        image_dict = {}
        network_dict = {}
        keypairs_dict = {}
        vm_dict = {}

        if os_config:
            os_conn_config = os_config.get('connection')

            # Setup proxy settings if any
            if os_conn_config.get('http_proxy'):
                os.environ['HTTP_PROXY'] = os_conn_config['http_proxy']

            # Create images
            image_dict = create_images(os_conn_config, os_config.get('images'))

            # Create network
            network_dict = create_networks(os_conn_config, os_config.get('networks'))

            # Create keypairs
            keypairs_dict = create_keypairs(os_conn_config, os_config.get('keypairs'))

            # Create instance
            # instances_config = os_config.get('instances')
            # instance_config = None
            vm_dict = create_instances(os_conn_config, os_config.get('instances'), image_dict, network_dict,
                                       keypairs_dict)
            logger.info('Completed creating all configured instances')

            # TODO - Need to support other Linux flavors!
            logger.info('Configuring RPM NICs where required')
            for vm in vm_dict.itervalues():
                vm.config_rpm_nics()
            logger.info('Completed RPM NIC configuration')

        # Must enter either block
        if arguments.clean is not ARG_NOT_SET:
            # Clean environment
            for key, vm_inst in vm_dict.iteritems():
                vm_inst.clean()
            for key, kp_inst in keypairs_dict.iteritems():
                kp_inst.clean()
            for key, net_inst in network_dict.iteritems():
                net_inst.clean()
            if arguments.clean_image is not ARG_NOT_SET:
                for key, image_inst in image_dict.iteritems():
                    image_inst.clean()
        elif arguments.deploy is not ARG_NOT_SET:
            # Provision VMs
            ansible_config = config.get('ansible')
            if ansible_config and vm_dict:
                if not __apply_ansible_playbooks(ansible_config, vm_dict):
                    logger.error("Problem applying ansible playbooks")
    else:
        logger.error('Unable to read configuration file - ' + arguments.environment)
        exit(1)
    exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--deploy', dest='deploy', nargs='?', default=ARG_NOT_SET,
                        help='When used, environment will be deployed and provisioned')
    parser.add_argument('-c', '--clean', dest='clean', nargs='?', default=ARG_NOT_SET,
                        help='When used, the environment will be removed')
    parser.add_argument('-i', '--clean-image', dest='clean_image', nargs='?', default=ARG_NOT_SET,
                        help='When cleaning, if this is set, the image will be cleaned too')
    parser.add_argument('-e', '--env', dest='environment', required=True,
                        help='The environment configuration YAML file - REQUIRED')
    args = parser.parse_args()

    if args.deploy is ARG_NOT_SET and args.clean is ARG_NOT_SET:
        print 'Must enter either -d for deploy or -c for cleaning up and environment'
        exit(1)
    if args.deploy is not ARG_NOT_SET and args.clean is not ARG_NOT_SET:
        print 'Cannot enter both options -d/--deploy and -c/--clean'
        exit(1)
    main(args)
