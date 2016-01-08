import os
import urllib2

"""
Utilities for basic file handling
"""


def file_exists(file_path):
    """
    Returns True if the image file already exists and throws an exception if the path is a directory
    :return:
    """
    if os.path.exists(file_path):
        if os.path.isdir(file_path):
            return False
        return os.path.isfile(file_path)
    return False


def download(url, dest_path):
    """
    Download a file to a destination path given a URL
    :rtype : File object
    """
    name = url.rsplit('/')[-1]
    dest = dest_path + '/' + name
    try:
        # Override proxy settings to use localhost to download file
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
        response = urllib2.urlopen(url)
    except (urllib2.HTTPError, urllib2.URLError):
        raise Exception

    with open(dest, 'wb') as f:
        f.write(response.read())
    return f
