# Model definitions for Model Hub application
# This file can contain model metadata classes if needed

class ModelMetadata:
    """Metadata for an uploaded model"""
    def __init__(self, name, description='', author=''):
        self.name = name
        self.description = description
        self.author = author
