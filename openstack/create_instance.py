import novaclient.v2.client as novaclient


class OpenStackVmInstance:
    """
    Class responsible for creating a VM instance in OpenStack
    """

    def __init__(self, username, password, os_auth_url, tenant_name, name, flavor, image, port):
        """
        Constructor
        :param username: The user to the OpenStack API
        :param password: The password to the OpenStack API
        :param os_auth_url: The URL to the OpenStack API
        :param tenant_name: The OpenStack tenant name
        :param name: The name of the OpenStack instance to be deployed
        :param flavor: The size of the VM to be deployed (i.e. 'm1.small')
        :param image: The OpenStack image on which to deploy the VM
        :param port: The OpenStack port to which to deploy the VM
        :raises Exception
        """
        self.name = name
        self.image = image
        self.port = port
        self.port_id = port.get('port').get('id')

        self.vm = None

        creds = {
            'username': username,
            'api_key': password,
            'auth_url': os_auth_url,
            'project_id': tenant_name,
        }
        self.nova = novaclient.Client(**creds)

        # Validate that the flavor is supported
        self.flavor = self.nova.flavors.find(name=flavor)
        if not self.flavor:
            raise Exception

    def create(self):
        """
        Creates a VM instance
        :return: The VM reference object
        """
        self.vm = self.nova.servers.create(
            name=self.name,
            flavor=self.flavor,
            image=self.image,
            nics=[{"port-id": self.port_id}])

    def clean(self):
        """
        Destroys the VM instance
        """
        if self.vm:
            self.nova.servers.delete(self.vm)
