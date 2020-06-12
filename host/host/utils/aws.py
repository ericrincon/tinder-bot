import boto3
import os
import uuid
import numpy as np

from io import StringIO, BytesIO
from PIL import Image

from host.host.config import Config


def upload_image(image_name: str):
    s3 = boto3.resource('s3')

    data = open('test.jpg', 'rb')

    s3.Bucket("tuser-image").put_object(Key=image_name, Body=data)


def s3_put_png(image: np.ndarray, image_name: str, key: str = None):
    s3 = boto3.resource("s3", aws_access_key_id=os.getenv("aws_access_key_id"),
                        aws_secret_access_key=os.getenv("aws_secret_access_key"))

    img = Image.fromarray(image)
    out_img = BytesIO()
    img.save(out_img, format='png')
    out_img.seek(0)

    if key is not None:
        key = "{}/{}".format(key, image_name)
    else:
        key = image_name

    response = s3.Bucket('tuser-image').put_object(Key=key, Body=out_img, ContentType='image/png')

    return key


def generate_video_face_image_name() -> str:
    return str(uuid.uuid4())
