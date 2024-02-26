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
        if aws_credentials is not None:
            try:
                # for case of secret
                aws_credentials = json.loads(aws_credentials)
                logger.info("Getting secrets keys")
            except json.JSONDecodeError:
                # for case of integration
                logger.info("Getting integration keys")
                decoded_bytes = base64.b64decode(aws_credentials)
                aws_credentials = decoded_bytes.decode("utf-8")
                aws_credentials = json.loads(aws_credentials)
                logger.info(f"integration_name = {integration_name}")
        else:
            # for local development
            logger.info("Getting secrets keys from local json")
            with open(os.path.join('..', 'aws-credentials.json')) as json_file:
                aws_credentials = json.load(json_file)

        self.aws_secret_access_key = aws_credentials['secret']
        self.aws_access_key_id = aws_credentials['key']
