import zipfile
import random
from logger import logger


def unzip_file_from_server_response(server_response, output_dir):
    try:
        zf = zipfile.ZipFile(server_response, 'r')
        filename = zf.namelist().pop()
        zf.extractall(output_dir)
        zf.close()
        return filename
    except:
        logger.error('unable to unzip server response. It is not a zip file')
        return None


def generate_password():
    pwd = ''
    characters = get_password_chars()
    for i in range(random.randrange(8, 12)):
        pwd += characters[random.randrange(len(characters))]
    return pwd


def get_password_chars():
    alphabet = 'abcdefghijklmnopqrstuvwxyx'
    return alphabet + alphabet.upper() + '0123456789' + '@_-()[]?='


