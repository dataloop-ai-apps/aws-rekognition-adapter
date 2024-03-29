import boto3
import botocore.exceptions
import dtlpy as dl
import logging
from modules.base_service_runner import RekognitionServiceRunner

logger = logging.getLogger(name=__name__)


class ServiceRunner(RekognitionServiceRunner):

    @staticmethod
    def auto_link_box_to_points(item: dl.Item):
        """
        A function to auto link point annotations to their parent box annotation.

        :param item: Dataloop item.
        """
        annotations = item.annotations.list()

        for box_annotation in annotations:
            if box_annotation.type == dl.AnnotationType.BOX:
                for point_annotation in annotations:
                    if point_annotation.type == dl.AnnotationType.POINT:
                        rule1 = box_annotation.left <= point_annotation.x <= box_annotation.right
                        rule2 = box_annotation.top <= point_annotation.y <= box_annotation.bottom
                        if rule1 and rule2:
                            point_annotation.parent_id = box_annotation.id
                            point_annotation.update(system_metadata=True)
                        else:
                            # Parenting a point if it is close enough one of the boxes
                            # Calculate the variation of 10% of the box sizes
                            box_width_variation = 0.1 * (box_annotation.right - box_annotation.left)
                            box_height_variation = 0.1 * (box_annotation.bottom - box_annotation.top)

                            # Define the region around the box
                            left_boundary = box_annotation.left - box_width_variation
                            right_boundary = box_annotation.right + box_width_variation
                            top_boundary = box_annotation.top - box_height_variation
                            bottom_boundary = box_annotation.bottom + box_height_variation

                            # Check if the point annotation is close enough to the box but not within the box
                            close_to_box = (
                                    left_boundary <= point_annotation.x <= right_boundary
                                    and top_boundary <= point_annotation.y <= bottom_boundary
                            )

                            if close_to_box:
                                point_annotation.parent_id = box_annotation.id
                                point_annotation.update(system_metadata=True)

        print(f'Auto linked all points that are inside of a box')

    def recognize_celebrities(self, item: dl.Item, context: dl.Context):
        """
        Object Detection using AWS Rekognition - recognize celebrities model.

        :param item: Dataloop item.
        :param context: Dataloop context to set the threshold
        """

        node = context.node
        threshold = node.metadata['customNodeConfig']['threshold']
        threshold = threshold * 100
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
            response = client.recognize_celebrities(Image=image)

        except botocore.exceptions.ClientError:
            logger.exception(msg=f"Couldn't detect moderation labels in {item.name}")
            raise

        print('Detected celebrities faces for ' + item.name)
        builder = item.annotations.builder()
        labels = set()
        for celebrity in response['CelebrityFaces']:
            print('Name: ' + celebrity['Name'])
            print('Id: ' + celebrity['Id'])
            print('KnownGender: ' + celebrity['KnownGender']['Type'])
            print('Smile: ' + str(celebrity['Face']['Smile']['Value']))
            print('Position:')
            print('   Left: ' + '{:.2f}'.format(celebrity['Face']['BoundingBox']['Height']))
            print('   Top: ' + '{:.2f}'.format(celebrity['Face']['BoundingBox']['Top']))
            print('Info')
            for url in celebrity['Urls']:
                print('   ' + url)
            print()

            if celebrity['MatchConfidence'] >= threshold:
                celebrity_face = celebrity['Face']
                # Points
                landmarks_annotations = celebrity_face['Landmarks']
                confidence = celebrity_face['Confidence'] / 100
                for landmarks_annotation in landmarks_annotations:
                    builder.add(annotation_definition=dl.Point(x=int(landmarks_annotation.get('X') * item.width),
                                                               y=int(landmarks_annotation.get('Y') * item.height),
                                                               label=landmarks_annotation.get('Type')),
                                model_info={'name': 'AWS Rekognition',
                                            'confidence': confidence})

                # Bounding Box
                left = int(celebrity_face['BoundingBox']['Left'] * item.width)
                top = int(celebrity_face['BoundingBox']['Top'] * item.height)
                right = left + int(celebrity_face['BoundingBox']['Width'] * item.width)
                bottom = top + int(celebrity_face['BoundingBox']['Height'] * item.height)
                label = celebrity['Name']

                builder.add(annotation_definition=dl.Box(top=top,
                                                         bottom=bottom,
                                                         left=left,
                                                         right=right,
                                                         label=label),
                            model_info={'name': 'AWS Rekognition', 'confidence': confidence})
                labels.add(label)

        annotations = item.annotations.upload(builder)
        logger.debug(f"{len(annotations)} Annotations has been uploaded")

        self.auto_link_box_to_points(item=item)

        return item
