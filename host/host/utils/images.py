import urllib.request
import numpy as np
import requests
import io

from PIL import Image
from urllib.error import URLError


def download_images(images):
    for image in images:
        download_image(image.url, image.file_path)


def download_image(url, file_name):
    try:
        urllib.request.urlretrieve(url=url, filename=file_name)
    except URLError as e:
        print("--------------------")
        print("Retrieving URL {} failed".format(url))
        print("Exception: {}".format(e))
        print("--------------------")


def get_image(url: str) -> np.ndarray:
    data = requests.get(url).content
    img = Image.open(io.BytesIO(data))
    img = np.asarray(img)

    return img
