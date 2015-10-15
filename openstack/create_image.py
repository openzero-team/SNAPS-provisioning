import logging
import file_utils
import os
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

    def __init__(self, username, password, os_auth_url, tenant_name, image_format, image_url, image_name, download_path):
        """Constructor"""
        self.username = username
        self.password = password
        self.os_auth_url = os_auth_url
        self.tenant_name = tenant_name
        self.image_format = image_format
        self.image_url = image_url
        self.image_name = image_name
        self.download_path = download_path

        filename = image_url.rsplit('/')[-1]
        self.image_file_path = download_path + '/' + filename

        self.image = None
        self.image_file = None

    def create(self):
        """
        Creates the image in OpenStack if it does not already exist
        :return: The OpenStack Image object
        """
        self.image_file = self.__get_image_file()
        glance = self.glance_client()
        self.image = glance.images.create(name=self.image_name, disk_format=self.image_format,
                                          container_format="bare", data=self.image_file.name)
        glance.images.upload(self.image.id, open(self.image_file.name, 'rb'))
        return self.image

    def clean(self):
        """
        Cleanse environment of all artifacts
        :return: void
        """
        if self.image:
            glance = self.glance_client()
            glance.images.delete(self.image.id)

        if self.image_file:
            shutil.rmtree(self.download_path)

    def glance_client(self):
        """
        Creates and returns a glance client object
        :return: the glance client
        """
        creds = self.__get_keystone_creds()
        keystone = ksclient.Client(**creds)
        glance_endpoint = keystone.service_catalog.url_for(service_type='image', endpoint_type='publicURL')
        auth = identity.Password(auth_url=self.os_auth_url, username=self.username, password=self.password,
                                 tenant_name=self.tenant_name)
        sess = session.Session(auth=auth)
        token = auth.get_token(sess)
        return Client('2', endpoint=glance_endpoint, token=token)

    def __get_image_file(self):
        """
        Returns True if the image file has already been downloaded
        :return: the image file object
        """
        if file_utils.file_exists(self.image_file_path):
            return open(self.image_file_path, 'r')
        else:
            if not os.path.exists(self.download_path):
                os.makedirs(self.download_path)
            return self.__download_image_file()

    def __get_keystone_creds(self):
        """
        Creates the object to hold the credentials for Keystone
        :return: the credentials
        """
        d = {'username': self.username, 'password': self.password, 'auth_url': self.os_auth_url,
             'tenant_name': self.tenant_name}
        return d

    def __download_image_file(self):
        """
        Downloads the image file
        :return: the image file object
        """
        if not file_utils.file_exists(self.image_file_path):
            return file_utils.download(self.image_url, self.download_path)
