import dtlpy as dl

from modules.detect_protective_equipment import detect_protective_equipment
from modules.detect_labels import detect_labels
from modules.face_detection import detect_faces

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


if __name__ == "__main__":
    dl.setenv('prod')

    # Dataloop only
    dataset = dl.projects.get(project_name="micha3").datasets.get(dataset_name="roni-no-aws")
    item = dataset.items.get(item_id="65c8d18068670b61ff2b7310")
    item_faces = dataset.items.get(item_id='65d45acc9e59d13ac297c81b')
    item_equip = dataset.items.get(item_id='65c8d189eab63a3de23aa720')
    test_detect_protective_equipment(item=item_equip, threshold=0.8)
    test_detect_labels(item=item, threshold=0.8)
    test_detect_faces(item=item_faces, threshold=0.8)

    # AWS bucket - in root
    dataset = dl.projects.get(project_name="micha3").datasets.get(dataset_name="roni-test-no-sync")
    item = dataset.items.get(item_id="65c8a57086cf45bc60fd92df")
    item_faces = dataset.items.get(item_id='65d45c0de26632e647c4a478')
    item_equip = dataset.items.get(item_id='65c8cdd186cf45ff7efd9daa')
    test_detect_protective_equipment(item=item_equip, threshold=0.8)
    test_detect_labels(item=item, threshold=0.8)
    test_detect_faces(item=item_faces, threshold=0.8)

    # AWS bucket - in folder
    dataset = dl.projects.get(project_name="micha3").datasets.get(dataset_name="roni-aws2")
    item = dataset.items.get(item_id='65c88539cd23c78d9c006ef0')
    item_faces = dataset.items.get(item_id='65c890b568670b97592b6139')
    item_equip = dataset.items.get(item_id='65c8854b92e33dc2f2e0feec')
    test_detect_protective_equipment(item=item_equip, threshold=0.8)
    test_detect_labels(item=item, threshold=0.8)
    test_detect_faces(item=item_faces, threshold=0.8)
