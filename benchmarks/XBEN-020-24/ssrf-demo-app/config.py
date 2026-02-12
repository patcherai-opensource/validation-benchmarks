import os


class Config:
    """MindsDB configuration."""
    STORAGE_DIR = os.environ.get('MINDSDB_STORAGE_DIR', '/app/data')
    FILES_DIR = os.path.join(STORAGE_DIR, 'files')
    TMP_DIR = os.path.join(STORAGE_DIR, 'tmp')
    CLOUD = os.environ.get('MINDSDB_CLOUD', 'true').lower() == 'true'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
