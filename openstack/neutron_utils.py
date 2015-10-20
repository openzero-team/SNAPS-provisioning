import logging
from neutronclient.v2_0 import client as neutronclient

logger = logging.getLogger('neutron_utils')

"""
Utilities for basic neutron API calls
"""


def neutron_client(username, password, os_auth_url, tenant_name):
    """
    Instantiates and returns a client for communications with OpenStack's Neutron server
    :param username: the username for connecting to the OpenStack remote API
    :param password: the password for connecting to the OpenStack remote API
    :param os_auth_url: the endpoint for connecting to the OpenStack remote API
    :param tenant_name: the tenant name for connecting to the OpenStack remote API
    :return: the client object
    """
    return neutronclient.Client(**{
        'username': username,
        'password': password,
        'auth_url': os_auth_url,
        'tenant_name': tenant_name})


def create_network(neutron, network_name):
    """
    Creates a network for OpenStack
    :param neutron: the client
    :param network_name: the name of the network to create
    :return: the network object
    """
    if neutron:
        json_body = {'network': {'name': network_name,
                                 'admin_state_up': True}}
        return neutron.create_network(body=json_body)
    else:
        logger.error("No Neutron client, failed to create network")
        raise Exception


def delete_network(neutron, network):
    """
    Deletes a network for OpenStack
    :param neutron: the client
    :param network: the network object
    """
    if neutron and network:
        neutron.delete_network(network['network']['id'])


def create_subnet(neutron, network, subnet_name, subnet_cidr):
    """
    Creates a network subnet for OpenStack
    :param neutron: the client
    :param network: the network object
    :param subnet_name: the name of the subnet object
    :param subnet_cidr: the subnet object's mask
    :return: the subnet object
    """
    if neutron and network:
        json_body = {'subnets': [{'name': subnet_name, 'cidr': subnet_cidr, 'ip_version': 4,
                                  'network_id': network['network']['id']}]}
        return neutron.create_subnet(body=json_body)
    else:
        logger.error("Cannot create subnet without a neutron client or network")
        raise Exception


def delete_subnet(neutron, subnet):
    """
    Deletes a network subnet for OpenStack
    :param neutron: the client
    :param subnet: the subnet object
    """
    if neutron and subnet:
        neutron.delete_subnet(subnet['subnets'][0]['id'])


def create_router(neutron, router_name):
    """
    Creates a router for OpenStack
    :param neutron: the client
    :param router_name: the name of the router to create
    :return: the router object
    """
    if neutron:
        json_body = {'router': {'name': router_name, 'admin_state_up': True}}
        return neutron.create_router(json_body)
    else:
        logger.error("Cannot create router without a neutron client")
        raise Exception


def delete_router(neutron, router):
    """
    Deletes a router for OpenStack
    :param neutron: the client
    :param router: the router object
    """
    if neutron and router:
        neutron.delete_router(router=router['router']['id'])
        return True


def add_interface_router(neutron, router, subnet):
    """
    Adds an interface router for OpenStack
    :param neutron: the client
    :param router: the router object
    :param subnet: the subnet object
    :return: the interface router object
    """
    if neutron and router and subnet:
        json_body = {"subnet_id": subnet['subnets'][0]['id']}
        return neutron.add_interface_router(router=router['router']['id'], body=json_body)
    else:
        logger.error("Unable to create interface router as neutron client, router or subnet were not created")
        raise Exception


def remove_interface_router(neutron, router, subnet):
    """
    Removes an interface router for OpenStack
    :param neutron: the client
    :param router: the router object
    :param subnet: the subnet object
    """
    if neutron and router and subnet:
        json_body = {"subnet_id": subnet['subnets'][0]['id']}
        neutron.remove_interface_router(router=router['router']['id'], body=json_body)

def create_port(neutron, name, network, ip):
    """
    Creates a port for OpenStack
    :param neutron: the client
    :param name: the port name
    :param network: the network object
    :param ip: the IP value
    :return: the port object
    """
    json_body = {'port': {
        'admin_state_up': True,
        'name': name,
        'network_id': network['network']['id'],
        'fixed_ips': [{"ip_address": ip}]
    }}

    return neutron.create_port(body=json_body)


def delete_port(neutron, port):
    """
    Removes an OpenStack port
    :param neutron: the client
    :param port: the port object
    :return:
    """
    neutron.delete_port(port['port']['id'])

