import json
import pickle
import logging

from app import app

log = logging.getLogger(__name__)


class XCom:
    """Cross-communication mechanism for tasks to exchange messages."""

    def __init__(self, row):
        self.id = row['id']
        self.key = row['key']
        self.value = row['value']
        self.timestamp = row['timestamp']
        self.execution_date = row['execution_date']
        self.task_id = row['task_id']
        self.dag_id = row['dag_id']
        self.run_id = row.get('run_id', '') if hasattr(row, 'get') else (row['run_id'] if 'run_id' in row.keys() else '')

    @staticmethod
    def deserialize_value(result):
        """Deserialize XCom value from database storage.

        When enable_xcom_pickling is False, values should be JSON-serialized.
        """
        enable_pickling = app.config.get('ENABLE_XCOM_PICKLING', False)

        if enable_pickling:
            try:
                return json.loads(result.value.decode('utf-8'))
            except Exception:
                return pickle.loads(result.value)
        else:
            try:
                return json.loads(result.value.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fallback for backwards compatibility with older data formats
                return pickle.loads(result.value)

    @staticmethod
    def serialize_value(value, serialize_as_pickle=False):
        """Serialize value for XCom storage."""
        if serialize_as_pickle:
            return pickle.dumps(value)
        return json.dumps(value).encode('utf-8')

    def to_dict(self):
        try:
            deserialized = XCom.deserialize_value(self)
            # Ensure the value is JSON-serializable
            if isinstance(deserialized, bytes):
                deserialized = deserialized.decode('utf-8', errors='replace')
        except Exception as e:
            log.warning("Failed to deserialize XCom value: %s", e)
            deserialized = "<deserialization error>"
        return {
            'key': self.key,
            'value': deserialized,
            'timestamp': self.timestamp,
            'execution_date': self.execution_date,
            'task_id': self.task_id,
            'dag_id': self.dag_id,
            'run_id': self.run_id,
        }


class DagModel:
    def __init__(self, row):
        self.dag_id = row['dag_id']
        self.description = row['description']
        self.schedule_interval = row['schedule_interval']
        self.is_paused = bool(row['is_paused'])
        self.is_active = bool(row['is_active'])
        self.last_parsed_time = row['last_parsed_time']
        self.fileloc = row['fileloc']
        self.owners = row['owners']

    def to_dict(self):
        return {
            'dag_id': self.dag_id,
            'description': self.description,
            'schedule_interval': self.schedule_interval,
            'is_paused': self.is_paused,
            'is_active': self.is_active,
            'last_parsed_time': self.last_parsed_time,
            'fileloc': self.fileloc,
            'owners': self.owners,
        }


class DagRun:
    def __init__(self, row):
        self.id = row['id']
        self.dag_id = row['dag_id']
        self.run_id = row['run_id']
        self.execution_date = row['execution_date']
        self.state = row['state']
        self.start_date = row['start_date']
        self.end_date = row['end_date']
        self.conf = row['conf']

    def to_dict(self):
        return {
            'dag_id': self.dag_id,
            'run_id': self.run_id,
            'execution_date': self.execution_date,
            'state': self.state,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }


class TaskInstance:
    def __init__(self, row):
        self.id = row['id']
        self.task_id = row['task_id']
        self.dag_id = row['dag_id']
        self.run_id = row['run_id']
        self.execution_date = row['execution_date']
        self.state = row['state']
        self.start_date = row['start_date']
        self.end_date = row['end_date']
        self.operator = row['operator']
        self.try_number = row['try_number']

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'dag_id': self.dag_id,
            'run_id': self.run_id,
            'execution_date': self.execution_date,
            'state': self.state,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'operator': self.operator,
            'try_number': self.try_number,
        }
