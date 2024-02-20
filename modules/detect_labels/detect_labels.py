import boto3
import botocore.exceptions
import dtlpy as dl
import logging

from modules.base_service_runner import RekognitionServiceRunner

logger = logging.getLogger(name=__name__)


class ServiceRunner(RekognitionServiceRunner):

    def aws_detect_labels(self, item: dl.Item, threshold=0.8):
        """
        Object Detection using AWS Rekognition - detect labels model.

        :param item: Dataloop item.
        :param threshold: A confidence threshold value for the detection.
        """
        driver = item.dataset.project.drivers.get(driver_id=item.dataset.driver)
        region = getattr(driver, 'region', 'eu-west-1')

        client = boto3.client('rekognition',
                              region_name=region,
                              aws_access_key_id=self.aws_access_key_id,
                              aws_secret_access_key=self.aws_secret_access_key)

        # If item is in S3 bucket - use the path
        logger.info(f"Driver path: {driver.path}, Driver type: {driver.type}")

        if driver.type == 's3':
            if driver.path is not None:
                image_path = driver.path + item.filename
                logger.info(f"Driver path is None. image_path: {image_path}")
            else:
                # driver path is the root
                image_path = item.filename[1:]
                logger.info(f"image_path: {image_path}")

            image = {'S3Object': {'Bucket': driver.bucket_name, 'Name': image_path}}

        # Else - use the item in dataloop dataset
        else:
            image_path = item.download()
            with open(image_path, 'rb') as img:
                image = {'Bytes': img.read()}

        try:
            response = client.detect_labels(Image=image,
                                            MinConfidence=threshold * 100)

            status_code = response['ResponseMetadata']['HTTPStatusCode']

            if 200 <= status_code < 300:
                logger.info(f"Response is OK! Status code: {status_code}")

            elif 400 <= status_code < 500:
                error_message = f"AWS service returned a client error with status code {status_code}"
                raise botocore.exceptions.ClientError(
                    error_response={'Error': {'Code': 'ClientError', 'Message': error_message}},
                    operation_name='DetectLabels')

            else:
                error_message = f"AWS service returned an error in response with status code {status_code}"
                raise Exception(error_message)

            print('Detected labels for ' + item.name)
            builder = item.annotations.builder()
            labels = set()
            for label in response['Labels']:
                if label['Confidence'] >= threshold:
                    for instance in label['Instances']:
                        bbox = instance['BoundingBox']
                        left = int(bbox['Left'] * item.width)
                        top = int(bbox['Top'] * item.height)
                        right = left + int(bbox['Width'] * item.width)
                        bottom = top + int(bbox['Height'] * item.height)
                        builder.add(annotation_definition=dl.Box(top=top,
                                                                 bottom=bottom,
                                                                 left=left,
                                                                 right=right,
                                                                 label=label['Name']),
                                    model_info={'name': 'WAS Rekognition', 'confidence': label['Confidence'] / 100})
                        labels.add(label['Name'])
            annotations = item.annotations.upload(builder)
            logger.debug(f"{len(annotations)} Annotations has been uploaded")

        except botocore.exceptions.ClientError as e:
            print("Client error:", e)

        except Exception as e:
            print("Unexpected error:", e)

