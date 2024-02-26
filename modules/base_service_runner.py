import os
import dtlpy as dl
import logging
import json
import base64

logger = logging.getLogger(name=__name__)


class RekognitionServiceRunner(dl.BaseServiceRunner):
    """

    A class to handle various detection models using AWS Rekognition API.

    """

    def __init__(self, integration_name):
        aws_credentials = os.environ.get(integration_name.replace('-', '_'), None)
        logger.info("Getting integration keys")

        decoded_bytes = base64.b64decode(aws_credentials)
        aws_credentials = decoded_bytes.decode("utf-8")
        aws_credentials = json.loads(aws_credentials)
        logger.info(f"integration_name = {integration_name}")

        self.aws_secret_access_key = aws_credentials['secret']
        self.aws_access_key_id = aws_credentials['key']
