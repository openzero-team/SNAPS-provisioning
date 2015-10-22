import logging
import file_utils
import os
import shutil
import glance_utils

logger = logging.getLogger('create_image')


class OpenStackImage:
    """
    Class responsible for creating an image in OpenStack
    """

    def __init__(self, os_creds, image_format, image_url, image_name, download_path):
        """
        Constructor
        :param os_creds: The OpenStack connection credentials
        :param image_format: The type of image file
        :param image_url: The download location of the image file
        :param image_name: The name to register the image
        :param download_path: The local filesystem location to where the image file will be downloaded
        :return:
        """
        self.os_creds = os_creds
        self.image_format = image_format
        self.image_url = image_url
        self.image_name = image_name
        self.download_path = download_path

        filename = image_url.rsplit('/')[-1]
        self.image_file_path = download_path + '/' + filename

        self.image = None
        self.image_file = None
        self.glance = glance_utils.glance_client(os_creds)

    def create(self):
        """
        Creates the image in OpenStack if it does not already exist
        :return: The OpenStack Image object
        """
        import nova_utils
        nova = nova_utils.nova_client(self.os_creds)
        image_dict = None
        try:
            image_dict = nova.images.find(name=self.image_name)
        except:
            logger.info('No existing image found with name - ' + self.image_name)
            pass

        if image_dict:
            self.image = self.glance.images.get(image_dict.id)
            if self.image:
                logger.info('Found image with name - ' + self.image_name)
                return self.image

        self.image_file = self.__get_image_file()
        self.image = self.glance.images.create(name=self.image_name, disk_format=self.image_format,
                                               container_format="bare", data=self.image_file.name)
        self.glance.images.upload(self.image.id, open(self.image_file.name, 'rb'))
        return self.image

    def clean(self):
        """
        Cleanse environment of all artifacts
        :return: void
        """
        if self.image:
            self.glance.images.delete(self.image['id'])

        if self.image_file:
            shutil.rmtree(self.download_path)

    def __get_image_file(self):
        """
        Returns the image file reference.
        If the image file does not exist, download it
        :return: the image file object
        """
        if file_utils.file_exists(self.image_file_path):
            return open(self.image_file_path, 'r')
        else:
            if not os.path.exists(self.download_path):
                os.makedirs(self.download_path)
            return self.__download_image_file()

    def __download_image_file(self):
        """
        Downloads the image file
        :return: the image file object
        """
        if not file_utils.file_exists(self.image_file_path):
            return file_utils.download(self.image_url, self.download_path)
