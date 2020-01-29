import boto3

from host.host.utils.config import Config


def upload_image(image_name: str):
    s3 = boto3.resource('s3')

    data = open('test.jpg', 'rb')

    s3.Bucket("tuser-image").put_object(Key=image_name, Body=data)