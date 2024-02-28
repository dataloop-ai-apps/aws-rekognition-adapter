import boto3
import botocore.exceptions
import dtlpy as dl
import logging
from modules.base_service_runner import RekognitionServiceRunner

logger = logging.getLogger(name='aws-rekognition')


class ServiceRunner(RekognitionServiceRunner):

    def detect_moderation_labels(self, item: dl.Item, context: dl.Context):
        """
        Object Detection using AWS Rekognition - detect protective equipment model.

        Detects moderation labels in the image. Moderation labels identify content
        that may be inappropriate for some audiences.


        :param item: Dataloop item.
        :param context: Dataloop context to set the threshold
        """
        node = context.node
        threshold = node.metadata['customNodeConfig']['threshold']
        threshold = threshold*100
        logger.info('threshold: {}'.format(threshold))

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
            response = client.detect_moderation_labels(Image=image)

        except botocore.exceptions.ClientError:
            logger.exception(msg=f"Couldn't detect moderation labels in {item.name}")
            raise

        print('Detected moderation labels for ' + item.name)
        builder = item.annotations.builder()
        labels = set()
        for label in response['ModerationLabels']:
            if label['Confidence'] >= threshold:
                builder.add(annotation_definition=dl.Classification(label=label['Name']),
                            model_info={'name': 'AWS Rekognition', 'confidence': label['Confidence'] / 100})
                labels.add(label['Name'])
        annotations = item.annotations.upload(builder)

        # Parenting
        sorted_annotations = sorted(response['ModerationLabels'], key=lambda x: x['TaxonomyLevel'])
        for sorted_annotation in sorted_annotations:
            parent_name = sorted_annotation['ParentName']
            if parent_name:
                # Find the parent annotation
                parent_annotation = next((a for a in annotations.annotations if a.label == parent_name), None)
                cur_annotations = next((a for a in annotations.annotations if a.label == sorted_annotation['Name']),
                                       None)
                if parent_annotation:
                    # Assign the parent's to the child
                    cur_annotations.parent_id = parent_annotation.id
                    cur_annotations.update(system_metadata=True)
        logger.debug(f"{len(annotations)} Annotations has been uploaded")

        return item
