import boto3
import botocore.exceptions
import dtlpy as dl
import logging
from modules.base_service_runner import RekognitionServiceRunner

logger = logging.getLogger(name=__name__)


class ServiceRunner(RekognitionServiceRunner):

    def detect_text(self, item: dl.Item, annotation_type, threshold=0.8):
        """
        Object Detection using AWS Rekognition - detect text model.

        :param annotation_type: set the type of annotation, either Box or Polygon
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
            response = client.detect_text(Image=image)

        except botocore.exceptions.ClientError:
            logger.exception(msg=f"Couldn't detect moderation labels in {item.name}")
            raise

        print('Detected text for ' + item.name)
        builder = item.annotations.builder()
        labels = set()
        text_detections = response['TextDetections']
        for text in text_detections:
            if text['Confidence'] >= threshold:
                text_geo = text['Geometry']
                # Bounding box
                if annotation_type == 'Box':
                    bbox = text_geo['BoundingBox']
                    left = int(bbox['Left'] * item.width)
                    top = int(bbox['Top'] * item.height)
                    right = left + int(bbox['Width'] * item.width)
                    bottom = top + int(bbox['Height'] * item.height)
                    builder.add(annotation_definition=dl.Box(top=top,
                                                             bottom=bottom,
                                                             left=left,
                                                             right=right,
                                                             label=text['DetectedText']),
                                model_info={'name': 'AWS Rekognition', 'confidence': text['Confidence'] / 100})
                    labels.add(text['DetectedText'])

                elif annotation_type == 'Polygon':
                    # Polygon
                    coordinates = [[point['X'] * item.width, point['Y'] * item.height] for point in text_geo['Polygon']]
                    builder.add(annotation_definition=dl.Polygon(geo=coordinates, label=text['DetectedText']),
                                model_info={'name': 'AWS Rekognition', 'confidence': text['Confidence'] / 100})

            annotations = item.annotations.upload(builder)
            logger.debug(f"{len(annotations)} Annotations has been uploaded")

        return item
