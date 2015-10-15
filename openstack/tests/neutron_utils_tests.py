import unittest
import openstack.neutron_utils as neutron_utils

# This is currently pointing to the CL OPNFV Lab 2 environment and these tests will break should there not be network
# connectivity to this location.
os_auth_url = 'http://10.197.123.37:5000/v2.0'

username = 'admin'
password = 'octopus'
tenant_name = 'admin'
network_name = 'test-neutron-utils-network'
subnet_name = 'test-neutron-utils-subnet'
router_name = 'test-neutron-utils-router'
subnet_cidr = '10.197.122.0/24'
port_name = 'test-port-name'
ip_1 = '10.197.122.100'
ip_2 = '10.197.122.200'


class NeutronUtilsTests(unittest.TestCase):
    """
    Test for the CreateImage class defined in create_image.py
    """

    def setUp(self):
        """
        Instantiates the CreateImage object that is responsible for downloading and creating an OS image file
        within OpenStack
        """
        self.neutron = neutron_utils.neutron_client(username, password, os_auth_url, tenant_name)
        self.network = None
        self.subnet = None
        self.port = None
        self.router = None
        self.interface_router = None

    def tearDown(self):
        """
        Cleans the remote OpenStack objects
        """
        if self.interface_router:
            neutron_utils.remove_interface_router(self.neutron, self.router, self.subnet)

        if self.router:
            neutron_utils.delete_router(self.neutron, self.router)
            validate_router(self.neutron, self.router.get('name'), False)

        if self.port:
            neutron_utils.delete_port(self.neutron, self.port)

        if self.subnet:
            neutron_utils.delete_subnet(self.neutron, self.subnet)
            validate_subnet(self.neutron, self.subnet.get('name'), subnet_cidr, False)

        if self.network:
            neutron_utils.delete_network(self.neutron, self.network)
            validate_network(self.neutron, self.network['network']['name'], False)

    def test_create_network(self):
        """
        Tests the neutron_utils.create_neutron_net() function
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

    def test_create_network_empty_name(self):
        """
        Tests the neutron_utils.create_neutron_net() function with an empty network name
        """
        self.network = neutron_utils.create_network(self.neutron, '')
        self.assertEqual('', self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, '', True))

    def test_create_network_null_name(self):
        """
        Tests the neutron_utils.create_neutron_net() function for an Exception when the network name is None
        """
        with self.assertRaises(Exception):
            self.network = neutron_utils.create_network(self.neutron, None)

    def test_create_subnet(self):
        """
        Tests the neutron_utils.create_neutron_net() function
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, subnet_name, subnet_cidr)
        validate_subnet(self.neutron, subnet_name, subnet_cidr, True)

    def test_create_subnet_null_name(self):
        """
        Tests the neutron_utils.create_neutron_subnet() function for an Exception when the subnet name is None
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        with self.assertRaises(Exception):
            neutron_utils.create_subnet(self.neutron, self.network, None, subnet_cidr)

    def test_create_subnet_empty_name(self):
        """
        Tests the neutron_utils.create_neutron_net() function with an empty name
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        neutron_utils.create_subnet(self.neutron, self.network, '', subnet_cidr)
        validate_subnet(self.neutron, '', subnet_cidr, True)

    def test_create_subnet_null_cidr(self):
        """
        Tests the neutron_utils.create_neutron_subnet() function for an Exception when the subnet CIDR value is None
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        with self.assertRaises(Exception):
            neutron_utils.create_subnet(self.neutron, self.network, subnet_name, None)

    def test_create_subnet_empty_cidr(self):
        """
        Tests the neutron_utils.create_neutron_subnet() function for an Exception when the subnet CIDR value is empty
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        with self.assertRaises(Exception):
            neutron_utils.create_subnet(self.neutron, self.network, subnet_name, '')

    def test_create_router(self):
        """
        Tests the neutron_utils.create_neutron_net() function
        """
        self.router = neutron_utils.create_router(self.neutron, router_name)
        validate_router(self.neutron, router_name, True)

    def test_create_router_empty_name(self):
        """
        Tests the neutron_utils.create_neutron_net() function
        """
        self.router = neutron_utils.create_router(self.neutron, '')
        validate_router(self.neutron, '', True)

    def test_create_router_null_name(self):
        """
        Tests the neutron_utils.create_neutron_subnet() function for an Exception when the subnet CIDR value is None
        """
        with self.assertRaises(Exception):
            self.router = neutron_utils.create_router(self.neutron, None)

    def test_add_interface_router(self):
        """
        Tests the neutron_utils.add_interface_router() function
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, subnet_name, subnet_cidr)
        validate_subnet(self.neutron, subnet_name, subnet_cidr, True)

        self.router = neutron_utils.create_router(self.neutron, router_name)
        validate_router(self.neutron, router_name, True)

        self.interface_router = neutron_utils.add_interface_router(self.neutron, self.router, self.subnet)
        validate_interface_router(self.interface_router, self.router, self.subnet)

    def test_add_interface_router_null_router(self):
        """
        Tests the neutron_utils.add_interface_router() function for an Exception when the router value is None
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, subnet_name, subnet_cidr)
        validate_subnet(self.neutron, subnet_name, subnet_cidr, True)

        with self.assertRaises(Exception):
            self.interface_router = neutron_utils.add_interface_router(self.neutron, self.router, self.subnet)

    def test_add_interface_router_null_subnet(self):
        """
        Tests the neutron_utils.add_interface_router() function for an Exception when the subnet value is None
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.router = neutron_utils.create_router(self.neutron, router_name)
        validate_router(self.neutron, router_name, True)

        with self.assertRaises(Exception):
            self.interface_router = neutron_utils.add_interface_router(self.neutron, self.router, self.subnet)

    def test_create_port(self):
        """
        Tests the neutron_utils.create_port() function
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, subnet_name, subnet_cidr)
        validate_subnet(self.neutron, subnet_name, subnet_cidr, True)

        self.port = neutron_utils.create_port(self.neutron, port_name, self.network, ip_1)
        validate_port(self.neutron, port_name, True)

    def test_create_port_empty_name(self):
        """
        Tests the neutron_utils.create_port() function
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, subnet_name, subnet_cidr)
        validate_subnet(self.neutron, subnet_name, subnet_cidr, True)

        self.port = neutron_utils.create_port(self.neutron, '', self.network, ip_1)
        validate_port(self.neutron, port_name, True)

    def test_create_port_null_name(self):
        """
        Tests the neutron_utils.create_port() function for an Exception when the port name value is None
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, subnet_name, subnet_cidr)
        validate_subnet(self.neutron, subnet_name, subnet_cidr, True)

        with self.assertRaises(Exception):
            self.port = neutron_utils.create_port(self.neutron, None, self.network, ip_1)

    def test_create_port_null_network_object(self):
        """
        Tests the neutron_utils.create_port() function for an Exception when the network object is None
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, subnet_name, subnet_cidr)
        validate_subnet(self.neutron, subnet_name, subnet_cidr, True)

        with self.assertRaises(Exception):
            self.port = neutron_utils.create_port(self.neutron, port_name, None, ip_1)

    def test_create_port_null_ip(self):
        """
        Tests the neutron_utils.create_port() function for an Exception when the IP value is None
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, subnet_name, subnet_cidr)
        validate_subnet(self.neutron, subnet_name, subnet_cidr, True)

        with self.assertRaises(Exception):
            self.port = neutron_utils.create_port(self.neutron, port_name, self.network, None)

    def test_create_port_invalid_ip(self):
        """
        Tests the neutron_utils.create_port() function for an Exception when the IP value is None
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, subnet_name, subnet_cidr)
        validate_subnet(self.neutron, subnet_name, subnet_cidr, True)

        with self.assertRaises(Exception):
            self.port = neutron_utils.create_port(self.neutron, port_name, self.network, 'foo')

    def test_create_port_invalid_ip_to_subnet(self):
        """
        Tests the neutron_utils.create_port() function for an Exception when the IP value is None
        """
        self.network = neutron_utils.create_network(self.neutron, network_name)
        self.assertEqual(network_name, self.network['network']['name'])
        self.assertTrue(validate_network(self.neutron, network_name, True))

        self.subnet = neutron_utils.create_subnet(self.neutron, self.network, subnet_name, subnet_cidr)
        validate_subnet(self.neutron, subnet_name, subnet_cidr, True)

        with self.assertRaises(Exception):
            self.port = neutron_utils.create_port(self.neutron, port_name, self.network, '10.197.123.100')


"""
Validation routines
"""


def validate_network(neutron, name, exists):
    """
    Returns true if a network for a given name DOES NOT exist if the exists parameter is false conversely true.
    Returns false if a network for a given name DOES exist if the exists parameter is true conversely false.
    :param neutron: The neutron client
    :param name: The expected network name
    :param exists: Whether or not the network name should exist or not
    :return: True/False
    """
    networks = neutron.list_networks()
    found = False
    for network, netInsts in networks.iteritems():
        for inst in netInsts:
            if inst.get('name') == name:
                found = True
    return exists == found


def validate_subnet(neutron, name, cidr, exists):
    """
    Returns true if a subnet for a given name DOES NOT exist if the exists parameter is false conversely true.
    Returns false if a subnet for a given name DOES exist if the exists parameter is true conversely false.
    :param neutron: The neutron client
    :param name: The expected subnet name
    :param cidr: The expected CIDR value
    :param exists: Whether or not the network name should exist or not
    :return: True/False
    """
    subnets = neutron.list_subnets()
    found = False
    for subnet, subInsts in subnets.iteritems():
        for inst in subInsts:
            if inst.get('name') == name and inst.get('cidr') == cidr:
                found = True
    return exists == found


def validate_router(neutron, name, exists):
    """
    Returns true if a router for a given name DOES NOT exist if the exists parameter is false conversely true.
    Returns false if a router for a given name DOES exist if the exists parameter is true conversely false.
    :param neutron: The neutron client
    :param name: The expected router name
    :param exists: Whether or not the network name should exist or not
    :return: True/False
    """
    routers = neutron.list_routers()
    found = False
    for router, routerInsts in routers.iteritems():
        for inst in routerInsts:
            if inst.get('name') == name:
                found = True
    return exists == found


def validate_interface_router(interface_router, router, subnet):
    """
    Returns true if the router ID & subnet ID have been properly included into the interface router object
    :param interface_router: the object to validate
    :param router: to validate against the interface_router
    :param subnet: to validate against the interface_router
    :return: True if both IDs match else False
    """
    subnet_id = interface_router.get('subnet_id')
    router_id = interface_router.get('port_id')

    return subnet.get('id') == subnet_id and router.get('id') == router_id


def validate_port(neutron, name, exists):
    """
    Returns true if a port for a given name DOES NOT exist if the exists parameter is false conversely true.
    Returns false if a port for a given name DOES exist if the exists parameter is true conversely false.
    :param neutron: The neutron client
    :param name: The expected router name
    :param exists: Whether or not the network name should exist or not
    :return: True/False
    """
    ports = neutron.list_ports()
    found = False
    for port, port_insts in ports.iteritems():
        for inst in port_insts:
            if inst.get('name') == name:
                found = True
    return exists == found
