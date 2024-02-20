import boto3
import botocore.exceptions
import dtlpy as dl
import logging
import json
from modules.base_service_runner import RekognitionServiceRunner

logger = logging.getLogger(name=__name__)


class ServiceRunner(RekognitionServiceRunner):

    def detect_faces(self, item: dl.Item, threshold=0.8):
        """
        Object Detection using AWS Rekognition - detect faces model.

        :param item: Dataloop item.
        :param threshold: A confidence threshold value for the detection.
        """
        threshold = threshold * 100
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
            response = client.detect_faces(Image=image, Attributes=['ALL'])
            status_code = response['ResponseMetadata']['HTTPStatusCode']

            if 200 <= status_code < 300:
                logger.info(f"Response is OK! Status code: {status_code}")

            elif 400 <= status_code < 500:
                error_message = f"AWS service returned a client error with status code {status_code}"
                raise botocore.exceptions.ClientError(
                    error_response={'Error': {'Code': 'ClientError', 'Message': error_message}},
                    operation_name='DetectProtectiveEquipment')

            else:
                error_message = f"AWS service returned an error in response with status code {status_code}"
                raise Exception(error_message)

            print('Detected faces for ' + item.name)
            builder = item.annotations.builder()
            labels = set()

            for face_detail in response['FaceDetails']:
                print('The detected face is between ' + str(face_detail['AgeRange']['Low'])
                      + ' and ' + str(face_detail['AgeRange']['High']) + ' years old')

                print('Here are the attributes:')
                print(json.dumps(face_detail, indent=4, sort_keys=True))

                # Example of Access attributes predictions for individual face details and print them
                print("Gender: " + str(face_detail['Gender']))
                print("Smile: " + str(face_detail['Smile']))
                print("Eyeglasses: " + str(face_detail['Eyeglasses']))
                print("Face Occluded: " + str(face_detail['FaceOccluded']))
                print("Emotions: " + str(face_detail['Emotions'][0]))

                if face_detail['Confidence'] >= threshold:
                    # Points
                    landmarks_annotations = face_detail['Landmarks']
                    for landmarks_annotation in landmarks_annotations:
                        builder.add(annotation_definition=dl.Point(x=int(landmarks_annotation.get('X') * item.width),
                                                                   y=int(landmarks_annotation.get('Y') * item.height),
                                                                   label=landmarks_annotation.get('Type')),
                                    model_info={'name': 'AWS Rekognition',
                                                'confidence': face_detail['Confidence'] / 100})

                    # Bounding Box
                    left = int(face_detail['BoundingBox']['Left'] * item.width)
                    top = int(face_detail['BoundingBox']['Top'] * item.height)
                    right = left + int(face_detail['BoundingBox']['Width'] * item.width)
                    bottom = top + int(face_detail['BoundingBox']['Height'] * item.height)
                    label = face_detail['Gender']['Value']
                    confidence = face_detail['Confidence'] / 100
                    builder.add(annotation_definition=dl.Box(top=top,
                                                             bottom=bottom,
                                                             left=left,
                                                             right=right,
                                                             label=label),
                                model_info={'name': 'AWS Rekognition', 'confidence': confidence})
                    labels.add(label)

            annotations = item.annotations.upload(builder)
            logger.debug(f"{len(annotations)} Annotations has been uploaded")

        except botocore.exceptions.ClientError as e:
            print("Client error:", e)

        except Exception as e:
            print("Unexpected error:", e)
