import dtlpy as dl

from modules.detect_protective_equipment import detect_protective_equipment
from modules.detect_labels import detect_labels
from modules.face_detection import detect_faces
from modules.detect_content_moderation import detect_content_moderation
from modules.detect_text import detect_text
from modules.recognize_celebrities import recognize_celebrities

integration_name = 'aws-integration'


def test_detect_protective_equipment(item: dl.Item, threshold=0.8):
    s = detect_protective_equipment.ServiceRunner(integration_name=integration_name)
    s.detect_protective_equipment(item=item, threshold=threshold)


def test_detect_labels(item: dl.Item, threshold=0.8):
    s = detect_labels.ServiceRunner(integration_name=integration_name)
    s.aws_detect_labels(item=item, threshold=threshold)


def test_detect_faces(item: dl.Item, threshold=0.8):
    s = detect_faces.ServiceRunner(integration_name=integration_name)
    s.detect_faces(item=item, threshold=threshold)


def test_detect_moderation_labels(item: dl.Item, threshold=0.8):
    s = detect_content_moderation.ServiceRunner(integration_name=integration_name)
    s.detect_moderation_labels(item=item, threshold=threshold)


def test_detect_text(item: dl.Item, annotation_type, threshold=0.8):
    s = detect_text.ServiceRunner(integration_name=integration_name)
    s.detect_text(item=item, annotation_type=annotation_type, threshold=threshold)


def test_recognize_celebrities(item: dl.Item, threshold=0.8):
    s = recognize_celebrities.ServiceRunner(integration_name=integration_name)
    s.recognize_celebrities(item=item, threshold=threshold)


if __name__ == "__main__":
    dl.setenv('prod')

    # Dataloop only
    dataset = dl.projects.get(project_name="micha3").datasets.get(dataset_name="roni-no-aws")
    item = dataset.items.get(item_id="65c8d18068670b61ff2b7310")
    item_faces = dataset.items.get(item_id='65d45acc9e59d13ac297c81b')
    item_equip = dataset.items.get(item_id='65c8d189eab63a3de23aa720')
    item_moderation = dataset.items.get(item_id='65d4d1890fbb2a5abe92a5ce')
    item_text = dataset.items.get(item_id='65d61d229e59d19b29999bf7')
    item_celebrities = dataset.items.get(item_id='65d74b1c0fbb2a0158940a64')

    test_detect_protective_equipment(item=item_equip, threshold=0.8)
    test_detect_labels(item=item, threshold=0.8)
    test_detect_faces(item=item_faces, threshold=0.8)
    test_detect_moderation_labels(item=item_moderation, threshold=0.8)
    test_detect_text(item=item_text, annotation_type='Polygon', threshold=0.8)
    test_recognize_celebrities(item=item_celebrities, threshold=0.8)

    # # AWS bucket - in root
    dataset = dl.projects.get(project_name="micha3").datasets.get(dataset_name="roni-test-no-sync")
    item = dataset.items.get(item_id="65c8a57086cf45bc60fd92df")
    item_faces = dataset.items.get(item_id='65d45c0de26632e647c4a478')
    item_equip = dataset.items.get(item_id='65c8cdd186cf45ff7efd9daa')
    item_moderation = dataset.items.get(item_id='65d4d17f9e59d1b10c98a188')
    item_text = dataset.items.get(item_id='65d76120f5ec3d1980be97d5')
    item_celebrities = dataset.items.get(item_id='65d74b4dc3e361b2bb429f8e')

    test_detect_protective_equipment(item=item_equip, threshold=0.8)
    test_detect_labels(item=item, threshold=0.8)
    test_detect_faces(item=item_faces, threshold=0.8)
    test_detect_moderation_labels(item=item_moderation, threshold=0.8)
    test_detect_text(item=item_text, annotation_type='Polygon', threshold=0.8)
    test_recognize_celebrities(item=item_celebrities, threshold=0.8)

    # # AWS bucket - in folder
    dataset = dl.projects.get(project_name="micha3").datasets.get(dataset_name="roni-aws2")
    item = dataset.items.get(item_id='65c88539cd23c78d9c006ef0')
    item_faces = dataset.items.get(item_id='65d7614952959e44d81a7060')
    item_equip = dataset.items.get(item_id='65c8854b92e33dc2f2e0feec')
    item_moderation = dataset.items.get(item_id='65d4d1730fbb2aff1c92a5c6')
    item_text = dataset.items.get(item_id='65d7615f202beb751575056d')
    item_celebrities = dataset.items.get(item_id='65d74b589607b456e71cb0d1')

    test_detect_protective_equipment(item=item_equip, threshold=0.8)
    test_detect_labels(item=item, threshold=0.8)
    test_detect_faces(item=item_faces, threshold=0.8)
    test_detect_moderation_labels(item=item_moderation, threshold=0.8)
    test_detect_text(item=item_text, annotation_type='Polygon', threshold=0.8)
    test_recognize_celebrities(item=item_celebrities, threshold=0.8)

