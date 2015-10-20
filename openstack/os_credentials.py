class OSCreds:
    """
    Represents the credentials required to connect with OpenStack servers
    """

    def __init__(self, username, password, auth_url, tenant_name):
        self.username = username
        self.password = password
        self.auth_url = auth_url
        self.tenant_name = tenant_name
