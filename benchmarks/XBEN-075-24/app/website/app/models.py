import json
import pickle
import logging

logger = logging.getLogger(__name__)


class AppConfiguration:
    """Reads configuration from the app_config table."""

    _cache = {}

    @classmethod
    def get_boolean(cls, key, default=False):
        from app import get_db
        try:
            conn = get_db()
            row = conn.execute('SELECT value FROM app_config WHERE key=?', (key,)).fetchone()
            conn.close()
            if row:
                return row['value'].lower() in ('true', '1', 'yes')
        except Exception:
            pass
        return default

    @classmethod
    def get_string(cls, key, default=''):
        from app import get_db
        try:
            conn = get_db()
            row = conn.execute('SELECT value FROM app_config WHERE key=?', (key,)).fetchone()
            conn.close()
            if row:
                return row['value']
        except Exception:
            pass
        return default


class TaskResult:
    """Handles serialization/deserialization of task result values."""

    @staticmethod
    def serialize_value(value):
        """Serialize task result value to bytes."""
        if AppConfiguration.get_boolean('enable_result_pickling'):
            return pickle.dumps(value)
        try:
            return json.dumps(value).encode('utf-8')
        except (ValueError, TypeError) as exc:
            logger.error(
                "%s. If you are using pickle instead of JSON for task results, "
                "then you need to enable pickle support in the application "
                "configuration.", exc
            )
            raise

    @staticmethod
    def _restore_value(raw_value, use_orm_hooks=False):
        """Restore a task result value from its stored representation."""
        if raw_value is None:
            return None
        if AppConfiguration.get_boolean('enable_result_pickling'):
            try:
                return pickle.loads(raw_value)
            except pickle.UnpicklingError:
                return json.loads(raw_value.decode('utf-8'))
        else:
            try:
                return json.loads(raw_value.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(raw_value)

    @staticmethod
    def deserialize_value(raw_value):
        """Deserialize task result value from stored bytes."""
        return TaskResult._restore_value(raw_value, False)

    @staticmethod
    def orm_deserialize_value(raw_value):
        """Deserialize for ORM display contexts."""
        return TaskResult._restore_value(raw_value, True)
