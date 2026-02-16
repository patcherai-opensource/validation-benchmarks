import os
import uuid
import time
import threading
import hashlib
from collections import OrderedDict

# Data directory for persistent storage
DATASTORE_PATH = os.getenv("DATASTORE_PATH", "/opt/appdata")


class MonitorStore:
    """In-memory store for URL monitors with thread-safe access."""

    def __init__(self):
        self._monitors = OrderedDict()
        self._queue = []
        self._lock = threading.Lock()
        self._datastore_path = DATASTORE_PATH

    def add(self, url, label=""):
        monitor_id = str(uuid.uuid4())
        now = time.time()
        monitor = {
            "id": monitor_id,
            "url": url,
            "label": label or url[:80],
            "date_created": now,
            "last_checked": 0,
            "last_changed": 0,
            "last_error": None,
            "check_count": 0,
            "snapshot": None,
            "snapshot_text": None,
            "previous_hash": None,
            "status_code": 0,
            "paused": False,
        }
        with self._lock:
            self._monitors[monitor_id] = monitor
            self._queue.append(monitor_id)
        return monitor_id

    def get(self, monitor_id):
        with self._lock:
            return self._monitors.get(monitor_id)

    def get_all(self):
        with self._lock:
            return list(self._monitors.values())

    def delete(self, monitor_id):
        with self._lock:
            if monitor_id in self._monitors:
                del self._monitors[monitor_id]
                return True
            return False

    def enqueue(self, monitor_id):
        with self._lock:
            if monitor_id in self._monitors and monitor_id not in self._queue:
                self._queue.append(monitor_id)

    def dequeue(self):
        with self._lock:
            if self._queue:
                return self._queue.pop(0)
            return None

    def update_snapshot(self, monitor_id, content, status_code, error):
        with self._lock:
            monitor = self._monitors.get(monitor_id)
            if not monitor:
                return

            now = time.time()
            monitor["last_checked"] = now
            monitor["check_count"] += 1
            monitor["status_code"] = status_code

            if error:
                monitor["last_error"] = error
                return

            monitor["last_error"] = None

            if content is not None:
                new_hash = hashlib.md5(content.encode("utf-8", errors="replace")).hexdigest()
                if monitor["previous_hash"] != new_hash:
                    monitor["last_changed"] = now
                monitor["previous_hash"] = new_hash
                monitor["snapshot_text"] = content
