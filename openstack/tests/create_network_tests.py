import unittest
import openstack.create_network as create_network

# This is currently pointing to the CL OPNFV Lab 2 environment and these tests will break should there not be network
# connectivity to this location.
osAuthUrl = 'http://10.197.123.37:5000/v2.0'

username = 'admin'
password = 'octopus'
tenant_name = 'admin'
priv_net_name = 'test-priv-net'
priv_subnet_name = 'test-priv-subnet'
priv_subnet_cidr = '10.197.122.0/24'
router_name = 'test-router'


class CreateNetworkSuccessTests(unittest.TestCase):
    """
    Test for the CreateImage class defined in create_image.py
    """

    def setUp(self):
        """
        Instantiates the CreateImage object that is responsible for downloading and creating an OS image file
        within OpenStack
        """
        self.net_creator = create_network.CreateNetwork(username, password, osAuthUrl, tenant_name, priv_net_name,
                                                          priv_subnet_name, priv_subnet_cidr, router_name)

    def tearDown(self):
        """
        Cleans the image and downloaded image file
        """
        self.net_creator.clean()

    def test1(self):
        """
        Tests the creation of an OpenStack image when the download directory does not exist.
        """
        # Create Image
        self.net_creator.create()

        neutron = self.net_creator.neutron

        # Validate network
        networks = neutron.list_networks()
        found = False
        for network, netInsts in networks.iteritems():
            for inst in netInsts:
                if inst.get('name') == self.net_creator.priv_net_name:
                    found = True
        self.assertEquals(True, found)

        # Validate subnets
        subnets = neutron.list_subnets()
        found = False
        for subnet, subInsts in subnets.iteritems():
            for inst in subInsts:
                if inst.get('name') == self.net_creator.priv_subnet_name:
                    found = True
        self.assertEquals(True, found)

        # Validate subnets
        routers = neutron.list_routers()
        found = False
        for router, routerInsts in routers.iteritems():
            for inst in routerInsts:
                if inst.get('name') == self.net_creator.router_name:
                    found = True
        self.assertEquals(True, found)

        # TODO - Expand tests especially negative ones.
