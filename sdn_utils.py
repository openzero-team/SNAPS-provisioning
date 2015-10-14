import os
import urllib2


def fileExists(filePath):
    """
    Returns True if the image file already exists and throws an exception if the path is a directory
    :return:
    """
    if os.path.exists(filePath):
        if os.path.isdir(filePath):
            return False
        return os.path.isfile(filePath)
    return False


def download(url, dest_path):
    """
    Download a file to a destination path given a URL
    :rtype : File object
    """
    name = url.rsplit('/')[-1]
    dest = dest_path + '/' + name
    try:
        response = urllib2.urlopen(url)
    except (urllib2.HTTPError, urllib2.URLError):
        raise Exception

    with open(dest, 'wb') as f:
        f.write(response.read())
    return f
