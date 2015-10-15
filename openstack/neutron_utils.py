import logging
import os_utils
from neutronclient.v2_0 import client as neutronclient

logger = logging.getLogger('neutron_utils')

"""
Utilities for basic neutron API calls
"""


def neutron_client(username, password, os_auth_url, tenant_name):
    """
    Instantiates and returns a client for communications with OpenStack's Neutron server
    :return: the client object
    """
    creds = os_utils.get_credentials(username, password, os_auth_url, tenant_name)
    return neutronclient.Client(**creds)


def create_network(neutron, network_name):
    """
    Creates a network for OpenStack
    :return: the network object
    """
    if neutron:
        json_body = {'network': {'name': network_name,
                                 'admin_state_up': True}}
        try:
            return neutron.create_network(body=json_body)
        except:
            logger.error("Failed to create network")
            raise Exception
    else:
        logger.error("No Neutron client, failed to create network")
        raise Exception


def delete_network(neutron, network):
    """
    Deletes a network for OpenStack
    """
    if neutron and network:
        try:
            neutron.delete_network(network['network']['id'])
        except:
            logger.error("Failed to delete network")
            raise Exception


def create_subnet(neutron, network, subnet_name, subnet_cidr):
    """
    Creates a network subnet for OpenStack
    :return: the subnet object
    """
    if neutron and network:
        json_body = {'subnets': [{'name': subnet_name, 'cidr': subnet_cidr, 'ip_version': 4,
                                  'network_id': network['network']['id']}]}
        try:
            return neutron.create_subnet(body=json_body)
        except:
            logger.error("Failed to create subnet")
            raise Exception
    else:
        logger.error("Cannot create subnet without a neutron client or network")
        raise Exception


def delete_subnet(neutron, subnet):
    """
    Deletes a network subnet for OpenStack
    """
    if neutron and subnet:
        try:
            neutron.delete_subnet(subnet['subnets'][0]['id'])
        except:
            logger.error("Failed to delete subnet")
            raise Exception


def create_router(neutron, router_name):
    """
    Creates a router for OpenStack
    :return: the router object
    """
    if neutron:
        json_body = {'router': {'name': router_name, 'admin_state_up': True}}
        try:
            return neutron.create_router(json_body)
        except:
            logger.error("Failed to create router")
            raise Exception
    else:
        logger.error("Cannot create router without a neutron client")
        raise Exception


def delete_router(neutron, router):
    """
    Deletes a router for OpenStack
    """
    if neutron and router:
        try:
            neutron.delete_router(router=router['router']['id'])
            return True
        except:
            logger.error("Failed to delete router")
            raise Exception


def add_interface_router(neutron, router, subnet):
    """
    Adds an interface router for OpenStack
    :return: the interface router object
    """
    if neutron and router and subnet:
        json_body = {"subnet_id": subnet['subnets'][0]['id']}
        try:
            return neutron.add_interface_router(router=router['router']['id'], body=json_body)
        except:
            logger.error("Failed to add interface router")
            raise Exception
    else:
        logger.error("Unable to create interface router as neutron client, router or subnet were not created")
        raise Exception


def remove_interface_router(neutron, router, subnet):
    """
    Removes an interface router for OpenStack
    """
    if neutron and router and subnet:
        json_body = {"subnet_id": subnet['subnets'][0]['id']}
        try:
            neutron.remove_interface_router(router=router['router']['id'], body=json_body)
        except:
            logger.error("Failed to remove interface router")
            raise Exception
