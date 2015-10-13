import logging, sdn_utils, glanceclient
import os

logger = logging.getLogger('create_image')

class CreateImage():
    """
    Class responsible for creating an image in OpenStack
    """

    def __init__(self, name, url, format, destPath):
        """Constructor"""
        self.name = name
        self.url = url
        self.format = format
        self.destPath = destPath

        fileName = url.rsplit('/')[-1]
        self.imageFilePath = destPath + fileName

    def create(self):
        """
        Creates the image in OpenStack if it does not already exist
        :return: The OpenStack Image object
        """
        self.imageFile = self.__getImageFile()
        glance = glanceclient.Client('1')
        self.image = glance.images.create(name=self.name)
        self.image.update(data=self.imageFile)
        return self.image

    def cleanEnv(self):
        """
        Cleanse environment of all artifacts
        :return: void
        """
        self.image.delete()
        os.remove(self.imageFile.name)

    def __getImageFile(self):
        """
        Returns True if the image file has already been downloaded
        :return: the image file object
        """
        if not sdn_utils.fileExists(self.imageFilePath):
            return open(self.imageFilePath, 'r')
        else:
            return self.__downloadImageFile()

    def __downloadImageFile(self):
        """
        Downloads the image file
        :return: the image file object
        """
        if(not sdn_utils.fileExists(self.imageFilePath)):
            return sdn_utils.download(self.url, self.destPath)

