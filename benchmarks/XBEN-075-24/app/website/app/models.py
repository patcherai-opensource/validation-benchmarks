import os
import time
import uuid


class ModelProject:
    """Represents an ML model project with configuration and training artifacts."""

    def __init__(self, name, description="", task_type="classification"):
        self.id = uuid.uuid4().hex[:12]
        self.name = name
        self.description = description
        self.task_type = task_type
        self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.status = "initialized"

    def get_save_path(self, base_dir):
        return os.path.join(base_dir, self.id)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "created_at": self.created_at,
            "status": self.status,
        }


TASK_TYPES = [
    "classification",
    "regression",
    "object_detection",
    "named_entity_recognition",
    "text_similarity",
    "image_similarity",
    "feature_extraction",
]
