#!/usr/bin/python
#
# This script is responsible for deploying a VM running virtual CMTS emulator instances

import sys
import logging
import os

from openstack import os_credentials
from openstack import neutron_utils
from openstack import nova_utils
import file_utils

logger = logging.getLogger('deploy_vnfs')


def get_os_credentials(os_conn_config):
    return os_credentials.OSCreds(os_conn_config.get('username'),
                                  os_conn_config.get('password'),
                                  os_conn_config.get('auth_url'),
                                  os_conn_config.get('tenant_name'))


def create_image(os_conn_config, image_config):
    """
    Creates an image in OpenStack if necessary
    :param image_config: The image configuration
    :return: A reference to the image creator object from which the image object can be accessed
    """
    from openstack.create_image import OpenStackImage
    image_creator = OpenStackImage(get_os_credentials(os_conn_config),
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


def create_vm_instance(os_conn_config, instance_config, image, network_dict):
    """
    Creates a VM instance
    :param os_conn_config: The OpenStack credentials
    :param instance_config: The VM instance configuration
    :param image: The VM image
    :param network_dict: A dictionary of network objects returned by OpenStack where the key contains the network name.
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
    vm_inst = OpenStackVmInstance(os_creds, config['name'], config['flavor'], image_creator, ports, config.get('keypair_name'),
                                  config.get('floating_ip'))
    vm_inst.create()
    return vm_inst


def setup_host(instance, ansible_config):
    """
    Configures a VM instance to run the CMTS
    :param instance: The instance object to which the CMTS will be deployed
    :param ansible_config: The configuration setting to execute Ansible
    :return: ???
    """
    # Execute ansible to setup VM instance with a running CMTS emulator
    print instance
    print ansible_config


def main():
    """
    Will need to set environment variable ANSIBLE_HOST_KEY_CHECKING=False or ...
    Create a file located in /etc/ansible/ansible/cfg or ~/.ansible.cfg containing the following content:

    [defaults]
    host_key_checking = False
    :return: To the OS
    """
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Starting to Deploy')
    config = None
    if len(sys.argv) > 1:
        logger.info('Reading configuration')
        config = file_utils.read_yaml(sys.argv[1])

    if config:
        os_config = config.get('openstack')
        os_conn_config = os_config.get('connection')

        if os_conn_config.get('http_proxy'):
            os.environ['HTTP_PROXY'] = os_conn_config['http_proxy']

        # Create images
        images = {}
        images_config = os_config.get('images')
        if images_config:
            for image_config_dict in images_config:
                image_config = image_config_dict.get('image')
                if image_config and image_config.get('name'):
                    images[image_config['name']] = create_image(os_conn_config, image_config)

        # Create network
        network_dict = {}
        network_confs = os_config.get('networks')
        if network_confs:
            for network_conf in network_confs:
                net_name = network_conf['network']['name']
                network_dict[net_name] = create_network(os_conn_config, network_conf)

        # Create keypairs
        keypairs_dict = {}
        keypairs_config = os_config.get('keypairs')
        if keypairs_config:
            for keypair_dict in keypairs_config:
                keypair_config = keypair_dict['keypair']
                keypairs_dict[keypair_config['name']] = create_keypair(os_conn_config, keypair_config)

        # Create instance
        instances_config = os_config.get('instances')
        instance_config = None
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
                                                                             os_conn_config.get('tenant_name')))
                        inst_image = nova.images.find(name=instance.get('imageName'))
                    if inst_image:
                        vm_dict[instance['name']] = create_vm_instance(os_conn_config, instance_config,
                                                                       inst_image, network_dict)

        # Setup host by applying ansible scripts to complete the machine's provisioning
        if instance_config:
            setup_host(instance_config, config.get('ansible'))

        # print 'Number of arguments:', len(sys.argv), 'arguments.'
        # print 'Argument List:', str(sys.argv)
        # print 'Argument 2:', str(sys.argv[1])
    else:
        logger.error('Unable to read configuration file - ' + sys.argv[1])
        exit(1)
    exit(0)


if __name__ == '__main__':
    main()
