#!/usr/bin/python
#
# This script is responsible for deploying a VM running virtual CMTS emulator instances

import sys
import yaml
import logging
from openstack import os_credentials

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

    try:
        network_creator = OpenStackNetwork(os_credentials.OSCreds(os_conn_config.get('username'),
                                                                  os_conn_config.get('password'),
                                                                  os_conn_config.get('auth_url'),
                                                                  os_conn_config.get('tenant_name')),
                                           NetworkSettings(name=config.get('name')),
                                           SubnetSettings(config.get('subnet')),
                                           RouterSettings(config.get('router')))
        network_creator.create()
        return network_creator
    except:
        logger.error('Unable to create network with name - ' + config.get('name'))

    logger.info('Created network ')


def create_instance(os_conn_config, instance_config):
    """
    Creates a VM instance
    :param instance_config: The VM instance configuration
    :return: A reference to the VM instance object
    """
    print os_conn_config
    print instance_config


def config_cmts(instance, ansible_config):
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
        image = create_image(os_conn_config, os_config.get('image'))
        print image

        network_dict = dict()
        for network_conf in os_config['networks']:
            network_dict[network_conf.get('name')] = create_network(os_conn_config, network_conf)

        instances_config = os_config.get('instances')
        for instance in instances_config:
            create_instance(os_conn_config, instance)
            config_cmts(instance, config.get('ansible'))

            # print 'Number of arguments:', len(sys.argv), 'arguments.'
            # print 'Argument List:', str(sys.argv)
            # print 'Argument 2:', str(sys.argv[1])
    else:
        logger.error('Unable to read configuration file - ' + sys.argv[1])
        exit(1)
    exit(0)


if __name__ == '__main__':
    main()
