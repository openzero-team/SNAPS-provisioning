import os

def fileExists(filePath):
    """
    Returns True if the image file already exists and throws an exception if the path is a directory
    :return:
    """
    # try:
    if (os.path.exists(filePath)):
        if os.path.isdir(filePath):
            return False
        return os.path.isfile(filePath)
    return False
    # except:
    #     return False

