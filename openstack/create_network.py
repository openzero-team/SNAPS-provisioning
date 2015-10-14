import logging
from neutronclient.v2_0 import client as neutronclient

logger = logging.getLogger('NeutronNetwork')


class CreateNetwork:
    """
    Class responsible for creating a network in OpenStack

    All tasks have been designed after the vPing scenario in the OPNFV functest repository. We will want to make
    this class more flexible, expand it beyond the private network. Additionally, many of the private methods here
    should probably make their way into a file named something like neutron_utils.py.
    """

    def __init__(self, username, password, osAuthUrl, tenantName, privNetName, privSubName, privSubCidr, routerName):
        """Constructor"""
        self.username = username
        self.password = password
        self.osAuthUrl = osAuthUrl
        self.tenantName = tenantName
        self.privNetName = privNetName
        self.privSubName = privSubName
        self.privSubCidr = privSubCidr
        self.routerName = routerName
        self.neutron = None
        self.network = None
        self.subnet = None
        self.router = None

    def create(self):
        self.neutron = self.neutron_client()
        self.neutron.format = 'json'
        logger.info('Creating neutron network %s...' % self.privNetName)
        self.network = self.__create_neutron_net()
        logger.debug("Network '%s' created successfully" % self.network['network']['id'])
        logger.debug('Creating Subnet....')
        self.subnet = self.__create_neutron_subnet()

        logger.debug("Subnet '%s' created successfully" % self.subnet['subnets'][0]['id'])
        logger.debug('Creating Router...')
        self.router = self.__create_neutron_router()

        logger.debug("Router '%s' created successfully" % self.router['router']['id'])
        logger.debug('Adding router to subnet...')

        result = self.__add_interface_router()

        if not result:
            raise Exception

    def clean(self):
        self.__remove_interface_router()
        self.__delete_neutron_router()
        self.__delete_neutron_subnet()
        self.__delete_neutron_net()

    def neutron_client(self):
        """
        Instantiates and returns a client for communications with OpenStack's Neutron server
        :return: the client object
        """
        creds = self.__get_credentials()
        return neutronclient.Client(**creds)

    def __get_credentials(self):
        """
        Returns a creds dictionary object
        :return: the credentials
        """
        return {
            'username': self.username,
            'password': self.password,
            'auth_url': self.osAuthUrl,
            'tenant_name': self.tenantName,
        }

    def __create_neutron_net(self):
        """
        Creates a network for OpenStack
        TODO - Consider moving this to a utility script called neutron_util.py
        :return:
        """
        if self.neutron:
            json_body = {'network': {'name': self.privNetName,
                                     'admin_state_up': True}}
            try:
                return self.neutron.create_network(body=json_body)
            except:
                logger.error("Failed to create network")
                raise Exception
        else:
            logger.error("No Neutron client, failed to create network")
            raise Exception

    def __delete_neutron_net(self):
        """
        Deletes a network for OpenStack
        TODO - Consider moving this to a utility script called neutron_util.py
        :return:
        """
        if self.neutron and self.network:
            try:
                self.neutron.delete_network(self.network['network']['id'])
            except:
                logger.error("Failed to delete network")
                raise Exception

    def __create_neutron_subnet(self):
        """
        Creates a network subnet for OpenStack
        TODO - Consider moving this to a utility script called neutron_util.py
        :return:
        """
        if self.neutron and self.network:
            json_body = {'subnets': [{'name': self.privSubName, 'cidr': self.privSubCidr,
                                      'ip_version': 4, 'network_id': self.network['network']['id']}]}
            try:
                return self.neutron.create_subnet(body=json_body)
            except:
                logger.error("Failed to create subnet")
                raise Exception
        else:
            logger.error("Cannot create subnet without a neutron client or network")
            raise Exception

    def __delete_neutron_subnet(self):
        """
        Deletes a network subnet for OpenStack
        TODO - Consider moving this to a utility script called neutron_util.py
        :return:
        """
        if self.neutron and self.subnet:
            try:
                self.neutron.delete_subnet(self.subnet['subnets'][0]['id'])
            except:
                logger.error("Failed to delete subnet")
                raise Exception

    def __create_neutron_router(self):
        """
        Creates a router for OpenStack
        TODO - Consider moving this to a utility script called neutron_util.py
        :return:
        """
        if self.neutron:
            json_body = {'router': {'name': self.routerName, 'admin_state_up': True}}
            try:
                return self.neutron.create_router(json_body)
            except:
                logger.error("Failed to create router")
                raise Exception
        else:
            logger.error("Cannot create router without a neutron client")
            raise Exception

    def __delete_neutron_router(self):
        """
        Deletes a router for OpenStack
        TODO - Consider moving this to a utility script called neutron_util.py
        :return:
        """
        if self.neutron and self.router:
            try:
                self.neutron.delete_router(router=self.router['router']['id'])
                return True
            except:
                logger.error("Failed to delete router")
                raise Exception

    def __add_interface_router(self):
        """
        Adds an interface router for OpenStack
        TODO - Consider moving this to a utility script called neutron_util.py
        :return:
        """
        if self.neutron and self.router and self.subnet:
            json_body = {"subnet_id": self.subnet['subnets'][0]['id']}
            try:
                return self.neutron.add_interface_router(router=self.router['router']['id'], body=json_body)
            except:
                logger.error("Failed to add interface router")
                raise Exception
        else:
            logger.error("Unable to create interface router as neutron client, router or subnet were not created")
            raise Exception

    def __remove_interface_router(self):
        """
        Removes an interface router for OpenStack
        TODO - Consider moving this to a utility script called neutron_util.py
        :return:
        """
        if self.neutron and self.router and self.subnet:
            json_body = {"subnet_id": self.subnet['subnets'][0]['id']}
            try:
                self.neutron.remove_interface_router(router=self.router['router']['id'], body=json_body)
            except:
                logger.error("Failed to remove interface router")
                raise Exception
