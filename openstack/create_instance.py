import nova_utils


class OpenStackVmInstance:
    """
    Class responsible for creating a VM instance in OpenStack
    """

    def __init__(self, os_creds, name, flavor, image, ports):
        """
        Constructor
        :param os_creds: The connection credentials to the OpenStack API
        :param name: The name of the OpenStack instance to be deployed
        :param flavor: The size of the VM to be deployed (i.e. 'm1.small')
        :param image: The OpenStack image on which to deploy the VM
        :param ports: List of ports (NICs) to deploy to the VM
        :raises Exception
        """
        self.name = name
        self.image = image
        self.ports = ports
        self.vm = None
        self.nova = nova_utils.nova_client(os_creds)

        # Validate that the flavor is supported
        self.flavor = self.nova.flavors.find(name=flavor)
        if not self.flavor:
            raise Exception

    def create(self):
        """
        Creates a VM instance
        :return: The VM reference object
        """
        nics = []
        for port in self.ports:
            kv = dict()
            kv['port-id'] = port['port']['id']
            nics.append(kv)

        self.vm = self.nova.servers.create(
            name=self.name,
            flavor=self.flavor,
            image=self.image,
            nics=nics)
        return self.vm

    def clean(self):
        """
        Destroys the VM instance
        """
        if self.vm:
            self.nova.servers.delete(self.vm)
