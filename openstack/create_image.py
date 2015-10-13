import logging
import sdn_utils

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
        :return:void
        """
        if(self.__checkEnv()):
            logger.info('Environment already setup')
        else:
            print

    def cleanEnv(self):
        """
        Cleanse environment of all artifacts
        :return: void
        """
        print

    def __checkEnv(self):
        """
        Returns True if environment is setup as configured else False
        :return:boolean
        """
        return False

    def __checkForImage(self):
        """
        Returns True if the image file has already been downloaded
        :return:
        """
        return False

    def __downloadImageFile(self):
        """
        Downloads the image file
        :return: The fully qualified file object
        """
        if(sdn_utils.fileExists(self.imageFilePath)):
            print

