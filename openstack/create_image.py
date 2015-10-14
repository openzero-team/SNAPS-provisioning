import logging, sdn_utils, os
from glanceclient import Client
from keystoneclient.auth.identity import v2 as identity
from keystoneclient import session
import keystoneclient.v2_0.client as ksclient
import shutil

logger = logging.getLogger('create_image')


class CreateImage:
    """
    Class responsible for creating an image in OpenStack
    """

    def __init__(self, username, password, osAuthUrl, tenantName, format, imageUrl, imageName, destPath):
        """Constructor"""
        self.username = username
        self.password = password
        self.osAuthUrl = osAuthUrl
        self.tenantName = tenantName
        self.format = format
        self.imageUrl = imageUrl
        self.imageName = imageName
        self.destPath = destPath

        fileName = imageUrl.rsplit('/')[-1]
        self.imageFilePath = destPath + '/' + fileName

        self.image = None
        self.imageFile = None

    def create(self):
        """
        Creates the image in OpenStack if it does not already exist
        :return: The OpenStack Image object
        """
        self.imageFile = self.__getImageFile()
        glance = self.glanceClient()
        self.image = glance.images.create(name=self.imageName, disk_format=self.format,
                                          container_format="bare", data=self.imageFile.name)
        glance.images.upload(self.image.id, open(self.imageFile.name, 'rb'))
        return self.image

    def clean(self):
        """
        Cleanse environment of all artifacts
        :return: void
        """
        if self.image:
            glance = self.glanceClient()
            glance.images.delete(self.image.id)

        if self.imageFile:
            shutil.rmtree(self.destPath)

    def glanceClient(self):
        """
        Creates and returns a glance client object
        :return: the glance client
        """
        creds = self.__get_keystone_creds()
        keystone = ksclient.Client(**creds)
        glance_endpoint = keystone.service_catalog.url_for(service_type='image', endpoint_type='publicURL')
        auth = identity.Password(auth_url=self.osAuthUrl, username=self.username, password=self.password,
                                 tenant_name=self.tenantName)
        sess = session.Session(auth=auth)
        token = auth.get_token(sess)
        return Client('2', endpoint=glance_endpoint, token=token)

    def __getImageFile(self):
        """
        Returns True if the image file has already been downloaded
        :return: the image file object
        """
        if sdn_utils.fileExists(self.imageFilePath):
            return open(self.imageFilePath, 'r')
        else:
            if not os.path.exists(self.destPath):
                os.makedirs(self.destPath)
            return self.__downloadImageFile()

    def __get_keystone_creds(self):
        """
        Creates the object to hold the credentials for Keystone
        :return: the credentials
        """
        d = {'username': self.username, 'password': self.password, 'auth_url': self.osAuthUrl,
             'tenant_name': self.tenantName}
        return d

    def __downloadImageFile(self):
        """
        Downloads the image file
        :return: the image file object
        """
        if not sdn_utils.fileExists(self.imageFilePath):
            return sdn_utils.download(self.imageUrl, self.destPath)
