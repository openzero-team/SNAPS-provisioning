import unittest
import openstack.create_network as create_network
import neutron_utils_tests

# This is currently pointing to the CL OPNFV Lab 2 environment and these tests will break should there not be network
# connectivity to this location.
os_auth_url = 'http://10.197.123.37:5000/v2.0'

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
        self.net_creator = create_network.CreateNetwork(username, password, os_auth_url, tenant_name, priv_net_name,
                                                        priv_subnet_name, priv_subnet_cidr, router_name)

    def tearDown(self):
        """
        Cleans the image and downloaded image file
        """
        self.net_creator.clean()

        if self.net_creator.subnet:
            # Validate subnet has been deleted
            neutron_utils_tests.validate_subnet(self.net_creator.neutron, self.net_creator.priv_subnet_name,
                                                self.net_creator.priv_subnet_cidr, False)

        if self.net_creator.network:
            # Validate network has been deleted
            neutron_utils_tests.validate_network(self.net_creator.neutron, self.net_creator.priv_net_name, False)

    def test_create_network(self):
        """
        Tests the creation of an OpenStack network.
        """
        # Create Image
        self.net_creator.create()

        # Validate network was created
        neutron_utils_tests.validate_network(self.net_creator.neutron, self.net_creator.priv_net_name, True)

        # Validate subnets
        neutron_utils_tests.validate_subnet(self.net_creator.neutron, self.net_creator.priv_subnet_name,
                                            self.net_creator.priv_subnet_cidr, True)

        # Validate routers
        neutron_utils_tests.validate_router(self.net_creator.neutron, self.net_creator.router_name, True)

        # Validate interface routers
        neutron_utils_tests.validate_interface_router(self.net_creator.interface_router, self.net_creator.router,
                                                      self.net_creator.subnet)

        # TODO - Expand tests especially negative ones.
