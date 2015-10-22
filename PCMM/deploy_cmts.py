#!/usr/bin/python
#
# This script is responsible for deploying a VM running virtual CMTS emulator instances

import sys
import yaml
import logging
from openstack import os_credentials
from openstack import neutron_utils

logger = logging.getLogger('deploy_cmts')


def read_config(config_file_path):
    """
    Reads the config file
    :param config_file_path: The file path to config
    :return: The config
    """
    logger.info('Attempting to load configuration file - ' + config_file_path)
    with open(config_file_path) as config_file:
        config = yaml.safe_load(config_file)
        logger.info('Loaded configuration')
    config_file.close()
    logger.info('Closing configuration file')
    return config


def create_image(os_conn_config, image_config):
    """
    Creates an image in OpenStack if necessary
    :param image_config: The image configuration
    :return: A reference to the image creator object from which the image object can be accessed
    """
    from openstack.create_image import OpenStackImage
    image_creator = OpenStackImage(os_credentials.OSCreds(os_conn_config.get('username'),
                                                          os_conn_config.get('password'),
                                                          os_conn_config.get('auth_url'),
                                                          os_conn_config.get('tenant_name')),
                                   image_config.get('format'), image_config.get('download_url'),
                                   image_config.get('name'), image_config.get('local_download_path'))
    image_creator.create()
    return image_creator


def create_network(os_conn_config, network_config):
    """
    Creates a network on which the CMTSs can attach
    :param os_conn_config: The OpenStack credentials object
    :param network_config: The network configuration
    :return: A references to the network creator objects for each network from which network elements such as the
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
    network_creator = OpenStackNetwork(os_credentials.OSCreds(os_conn_config.get('username'),
                                                              os_conn_config.get('password'),
                                                              os_conn_config.get('auth_url'),
                                                              os_conn_config.get('tenant_name')),
                                       NetworkSettings(name=config.get('name')),
                                       SubnetSettings(config.get('subnet')),
                                       RouterSettings(config.get('router')))
    network_creator.create()
    logger.info('Created network ')
    return network_creator


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

    os_creds = os_credentials.OSCreds(os_conn_config['username'], os_conn_config['password'],
                                      os_conn_config['auth_url'], os_conn_config['tenant_name'])
    neutron = neutron_utils.neutron_client(os_creds)
    config = instance_config['instance']
    ports_config = config['ports']
    ports = list()

    for port_config in ports_config:
        network_name = port_config['port']['network_name']
        os_network_obj = network_dict.get(network_name)
        if os_network_obj:
            logger.info('Creating port [' + port_config['port']['name'] + '] for network name - ' + network_name)
            port_setting = PortSettings(port_config)
            ports.append(
                neutron_utils.create_port(neutron, port_setting, os_network_obj.network, os_network_obj.subnet))
        else:
            logger.warn('Cannot create port as associated network name of [' + network_name + '] not configured.')
            raise Exception

    return OpenStackVmInstance(os_creds, instance_config['instance']['name'], instance_config['instance']['flavor'],
                               image, ports)


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
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Starting to Deploy')
    config = None
    if len(sys.argv) > 1:
        logger.info('Reading configuration')
        config = read_config(sys.argv[1])

    if config:
        os_config = config.get('openstack')
        os_conn_config = os_config.get('connection')
        image_creator = create_image(os_conn_config, os_config.get('image'))

        network_dict = dict()
        network_confs = os_config['networks']
        for network_conf in network_confs:
            net_name = network_conf['network']['name']
            network_dict[net_name] = create_network(os_conn_config, network_conf)

        instances_config = os_config.get('instances')
        for instance_config in instances_config:
            vm_inst = create_vm_instance(os_conn_config, instance_config, image_creator.image, network_dict)
            vm_inst.create()
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
