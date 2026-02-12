"""
File-based tracking store, simplified implementation of MLflow's FileStore.
"""
import os
import json
import time
import threading


class FileStore:
    """
    Simple file-based implementation of the MLflow tracking store.
    Stores experiment and run metadata in JSON files under the root directory.
    """

    def __init__(self, root_directory, artifact_root):
        self.root_directory = os.path.abspath(root_directory)
        self.artifact_root = os.path.abspath(artifact_root)
        self._lock = threading.Lock()
        self._experiments = {}
        self._runs = {}
        self._next_id = 1

        os.makedirs(self.root_directory, exist_ok=True)
        os.makedirs(self.artifact_root, exist_ok=True)

        # Create default experiment
        if "0" not in self._experiments:
            self._experiments["0"] = {
                "experiment_id": "0",
                "name": "Default",
                "artifact_location": os.path.join(self.artifact_root, "0"),
                "lifecycle_stage": "active",
                "creation_time": int(time.time() * 1000),
                "last_update_time": int(time.time() * 1000),
                "tags": []
            }
            os.makedirs(os.path.join(self.artifact_root, "0"), exist_ok=True)

    def create_experiment(self, name, artifact_location="", tags=None):
        with self._lock:
            # Check for duplicate names
            for exp in self._experiments.values():
                if exp["name"] == name and exp["lifecycle_stage"] == "active":
                    raise ValueError(
                        f"Experiment(name={name}) already exists. "
                        f"Experiment names must be unique."
                    )

            experiment_id = str(self._next_id)
            self._next_id += 1

            if not artifact_location:
                artifact_location = os.path.join(self.artifact_root, experiment_id)

            experiment = {
                "experiment_id": experiment_id,
                "name": name,
                "artifact_location": artifact_location,
                "lifecycle_stage": "active",
                "creation_time": int(time.time() * 1000),
                "last_update_time": int(time.time() * 1000),
                "tags": tags or []
            }

            self._experiments[experiment_id] = experiment

            # Create artifact directory for local paths
            if not artifact_location.startswith(("s3://", "gs://", "wasbs://", "hdfs://")):
                try:
                    import urllib.parse
                    parsed = urllib.parse.urlparse(artifact_location)
                    if parsed.scheme in ("file", ""):
                        local_path = parsed.path if parsed.path else artifact_location
                        os.makedirs(local_path, exist_ok=True)
                except OSError:
                    pass

            return experiment_id

    def get_experiment(self, experiment_id):
        return self._experiments.get(str(experiment_id))

    def list_experiments(self):
        return [
            exp for exp in self._experiments.values()
            if exp["lifecycle_stage"] == "active"
        ]

    def delete_experiment(self, experiment_id):
        with self._lock:
            exp = self._experiments.get(str(experiment_id))
            if exp is None:
                return False
            exp["lifecycle_stage"] = "deleted"
            return True

    def create_run(self, experiment_id, run_id, run_data):
        with self._lock:
            self._runs[run_id] = run_data
            # Create artifact directory for the run
            artifact_uri = run_data["info"]["artifact_uri"]
            try:
                import urllib.parse
                parsed = urllib.parse.urlparse(artifact_uri)
                if parsed.scheme in ("file", ""):
                    local_path = parsed.path if parsed.path else artifact_uri
                    os.makedirs(local_path, exist_ok=True)
            except OSError:
                pass

    def get_run(self, run_id):
        return self._runs.get(run_id)

    def search_runs(self, experiment_ids=None):
        if not experiment_ids:
            return list(self._runs.values())
        return [
            run for run in self._runs.values()
            if run["info"]["experiment_id"] in experiment_ids
        ]
