#!/usr/bin/python
#
# This script is responsible for deploying a VM running virtual CMTS emulator instances

import sys
import yaml


def read_config(config_path):
    """
    Reads the config file
    :param config_path: The file path to config
    :return: The config
    """
    with open(config_path) as config_file:
        config = yaml.safe_load(config_file)
    config_file.close()
    return config


def create_image(image_config):
    """
    Creates an image in OpenStack if necessary
    :param image_config: The image configuration
    :return: A reference to the image object
    """
    print image_config
    # Check for OS for imgage existence
    # If exists return image data
    # Else, check for local image file copy
    # If not download
    # Create image in OS
    # return instance data


def create_network(network_config):
    """
    Creates a network on which the CMTSs can attach
    :param network_config: The network configuration
    :return: A reference to the network object
    """
    # Check for OS for network existence
    # If exists return network instance data
    # Else, create network and return instance data
    print network_config


def create_instance(instance_config):
    """
    Creates a VM instance
    :param instance_config: The VM instance configuration
    :return: A reference to the VM instance object
    """
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
    config = None
    if len(sys.argv) > 1:
        config = read_config(sys.argv[1])

    if config:
        os_config = config.get('openstack')
        print os_config
        create_image(os_config.get('image'))

        create_network(os_config.get('network'))

        instances_config = os_config.get('instances')
        for instance in instances_config.iteritems():
            create_instance(instance)
            config_cmts(instance, config.get('ansible'))

            # print 'Number of arguments:', len(sys.argv), 'arguments.'
            # print 'Argument List:', str(sys.argv)
            # print 'Argument 2:', str(sys.argv[1])
    else:
        exit(1)
    exit(0)


if __name__ == '__main__':
    main()
