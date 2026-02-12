import json
import os
import time
import uuid
import threading

DATASTORE_PATH = os.environ.get("DATASTORE_PATH", "/datastore")


class ChangeDetectionStore:
    """Simple in-memory store for watches, mimicking the real changedetection.io store."""

    lock = threading.Lock()

    def __init__(self):
        self.watches = {}
        self._load()

    def _watch_dir(self, watch_uuid):
        return os.path.join(DATASTORE_PATH, "watches", watch_uuid)

    def _load(self):
        watches_dir = os.path.join(DATASTORE_PATH, "watches")
        if not os.path.isdir(watches_dir):
            os.makedirs(watches_dir, exist_ok=True)
            return
        for d in os.listdir(watches_dir):
            meta_path = os.path.join(watches_dir, d, "meta.json")
            if os.path.isfile(meta_path):
                try:
                    with open(meta_path) as f:
                        self.watches[d] = json.load(f)
                except Exception:
                    pass

    def add_watch(self, url, tag=""):
        with self.lock:
            watch_uuid = str(uuid.uuid4())
            watch = {
                "uuid": watch_uuid,
                "url": url,
                "tag": tag,
                "title": "",
                "last_checked": 0,
                "last_changed": 0,
                "history": {},
                "fetch_time": 0.0,
                "last_error": None,
                "paused": False,
                "created": int(time.time()),
                "check_count": 0,
            }
            watch_dir = self._watch_dir(watch_uuid)
            os.makedirs(watch_dir, exist_ok=True)
            with open(os.path.join(watch_dir, "meta.json"), "w") as f:
                json.dump(watch, f)
            self.watches[watch_uuid] = watch
            return watch_uuid

    def get_watch(self, uuid):
        return self.watches.get(uuid)

    def get_all_watches(self):
        return dict(self.watches)

    def delete_watch(self, uuid):
        with self.lock:
            if uuid in self.watches:
                del self.watches[uuid]

    def update_watch(self, uuid, data):
        with self.lock:
            if uuid in self.watches:
                self.watches[uuid].update(data)
                watch_dir = self._watch_dir(uuid)
                os.makedirs(watch_dir, exist_ok=True)
                with open(os.path.join(watch_dir, "meta.json"), "w") as f:
                    json.dump(self.watches[uuid], f)

    def save_snapshot(self, uuid, content):
        with self.lock:
            if uuid in self.watches:
                watch_dir = self._watch_dir(uuid)
                os.makedirs(watch_dir, exist_ok=True)
                ts = str(int(time.time()))
                snap_path = os.path.join(watch_dir, "{}.txt".format(ts))
                with open(snap_path, "w") as f:
                    f.write(content)
                self.watches[uuid]["history"][ts] = snap_path
                self.watches[uuid]["last_checked"] = int(time.time())
                self.watches[uuid]["check_count"] += 1
                with open(os.path.join(watch_dir, "meta.json"), "w") as f:
                    json.dump(self.watches[uuid], f)
                return ts
        return None

    def get_latest_snapshot(self, uuid):
        watch = self.watches.get(uuid)
        if not watch or not watch.get("history"):
            return None
        latest_ts = max(watch["history"].keys())
        snap_path = watch["history"][latest_ts]
        if os.path.isfile(snap_path):
            with open(snap_path) as f:
                return f.read()
        return None
