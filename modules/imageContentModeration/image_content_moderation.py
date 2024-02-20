import boto3
import os
import dtlpy as dl


class ServiceRunner(dl.BaseServiceRunner):
    def __init__(self, aws_key_name, aws_secret_name):
        secret_1 = os.environ.get(aws_key_name)
        secret_2 = os.environ.get(aws_secret_name)
        print(secret_1)
        print(secret_2)
        self.client = boto3.client('rekognition',
                                   region_name='eu-west-1',
                                   aws_access_key_id=secret_1,
                                   aws_secret_access_key=secret_2)

    def detect_moderation_labels(self, item):
        image_path = item.download()
        with open(image_path, 'rb') as image:
            response = self.client.detect_moderation_labels(Image={'Bytes': image.read()})
        item.metadata["contentModerationDetection"] = response["ModerationLabels"]
        item.update()
