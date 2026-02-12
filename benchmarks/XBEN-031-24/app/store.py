"""
MLflow FileStore implementation for experiment and model tracking.
"""
import json
import os
import shutil
import time
import uuid
import logging
from urllib.parse import urlparse, unquote, parse_qs

logger = logging.getLogger("mlflow.store")


def _generate_unique_id():
    return str(uuid.uuid4().hex[:12])


def _validate_experiment_name(name):
    if not name or not isinstance(name, str):
        raise ValueError("Invalid experiment name.")
    if name.startswith("/"):
        raise ValueError("Experiment name cannot start with '/'.")
    return name.strip()


def _decode(value):
    """Decode URL-encoded string."""
    if not value:
        return value
    return unquote(value)


def validate_query_string(query):
    """
    Validate that a query string does not contain path traversal sequences.
    Block query strings containing traversal paths (../) as they could be
    resolved as part of the path and allow path traversal.
    """
    query = _decode(query)
    if ".." in query:
        raise ValueError("Invalid query string: path traversal not allowed.")


def _is_local_uri(uri):
    """Returns True if the specified URI is a local file path or file:// URI."""
    parsed = urlparse(uri)
    if parsed.hostname and not (
        parsed.hostname == "."
        or parsed.hostname.startswith("localhost")
        or parsed.hostname.startswith("127.0.0.1")
    ):
        return False
    return parsed.scheme in ("", "file")


def _is_file_uri(uri):
    """Returns True if the URI uses the file:// scheme."""
    return urlparse(uri).scheme == "file"


def _local_file_uri_to_path(uri):
    """Convert a local file:// URI to a filesystem path."""
    parsed = urlparse(uri)
    path = parsed.path
    return os.path.normpath(path) if path else ""


def _resolve_artifact_location(artifact_uri, default_root):
    """
    Resolve an artifact URI to a filesystem path.
    Validates the URI for safety before resolving.
    """
    if artifact_uri is None:
        return default_root

    parsed = urlparse(artifact_uri)

    # Validate query string to prevent path traversal via query parameters
    validate_query_string(parsed.query)

    # Handle file:// URIs and bare paths
    if parsed.scheme == "file" or parsed.scheme == "":
        path = parsed.path
        if not path:
            raise ValueError("Artifact location path cannot be empty.")
        return os.path.normpath(path)

    # For remote schemes (s3, gs, hdfs, etc.), return as-is
    if parsed.scheme in ("s3", "gs", "hdfs", "wasbs", "dbfs"):
        return artifact_uri

    raise ValueError(
        f"Unsupported artifact location scheme: {parsed.scheme}. "
        f"Supported schemes: file, s3, gs, hdfs, wasbs, dbfs."
    )


def _resolve_source_uri(source_uri):
    """
    Resolve a model source URI to a path.
    Validates the URI for safety before resolving.
    """
    if not source_uri:
        raise ValueError("Source URI cannot be empty.")

    parsed = urlparse(source_uri)

    # Validate query string to prevent path traversal
    validate_query_string(parsed.query)

    if parsed.scheme == "file" or parsed.scheme == "":
        path = parsed.path
        if not path:
            raise ValueError("Source path cannot be empty.")
        return os.path.normpath(path)

    if parsed.scheme in ("s3", "gs", "hdfs", "wasbs", "dbfs", "runs", "models"):
        return source_uri

    raise ValueError(
        f"Unsupported source URI scheme: {parsed.scheme}."
    )


class FileStore:
    """
    File-based backend store for MLflow entities and metadata.
    """

    def __init__(self, root_directory, artifact_root):
        self.root_directory = root_directory
        self.artifact_root = artifact_root
        self._experiments = {}
        self._runs = {}
        self._registered_models = {}
        self._model_versions = {}
        self._next_experiment_id = 1
        self._init_default_experiment()

    def _init_default_experiment(self):
        default_artifact_path = os.path.join(self.artifact_root, "0")
        os.makedirs(default_artifact_path, exist_ok=True)
        self._experiments["0"] = {
            "experiment_id": "0",
            "name": "Default",
            "artifact_location": default_artifact_path,
            "lifecycle_stage": "active",
            "creation_time": int(time.time() * 1000),
            "last_update_time": int(time.time() * 1000),
            "tags": []
        }

    def create_experiment(self, name, artifact_location=None, tags=None):
        _validate_experiment_name(name)

        # Check for duplicate names
        for exp in self._experiments.values():
            if exp["name"] == name and exp["lifecycle_stage"] == "active":
                raise FileExistsError(f"Experiment(name={name}) already exists.")

        experiment_id = str(self._next_experiment_id)
        self._next_experiment_id += 1

        if artifact_location:
            resolved_location = _resolve_artifact_location(
                artifact_location, 
                os.path.join(self.artifact_root, experiment_id)
            )
        else:
            resolved_location = os.path.join(self.artifact_root, experiment_id)

        # Create the artifact directory for the experiment
        try:
            os.makedirs(resolved_location, exist_ok=True)
        except OSError:
            # If we cannot create the directory (e.g., file:///etc/passwd),
            # we still record the experiment metadata
            pass

        self._experiments[experiment_id] = {
            "experiment_id": experiment_id,
            "name": name,
            "artifact_location": resolved_location,
            "lifecycle_stage": "active",
            "creation_time": int(time.time() * 1000),
            "last_update_time": int(time.time() * 1000),
            "tags": tags or []
        }

        logger.info(f"Created experiment '{name}' with id={experiment_id}, "
                     f"artifact_location={resolved_location}")

        return experiment_id

    def get_experiment(self, experiment_id):
        return self._experiments.get(str(experiment_id))

    def search_experiments(self):
        return [
            exp for exp in self._experiments.values()
            if exp["lifecycle_stage"] == "active"
        ]

    def delete_experiment(self, experiment_id):
        experiment_id = str(experiment_id)
        if experiment_id not in self._experiments:
            return False
        self._experiments[experiment_id]["lifecycle_stage"] = "deleted"
        self._experiments[experiment_id]["last_update_time"] = int(time.time() * 1000)
        return True

    def create_run(self, experiment_id, user_id="", run_name="",
                   start_time=None, tags=None):
        run_id = _generate_unique_id()
        experiment = self.get_experiment(experiment_id)

        artifact_uri = os.path.join(
            experiment["artifact_location"], run_id, "artifacts"
        )

        run = {
            "info": {
                "run_id": run_id,
                "run_uuid": run_id,
                "experiment_id": str(experiment_id),
                "user_id": user_id,
                "status": "RUNNING",
                "start_time": start_time or int(time.time() * 1000),
                "end_time": None,
                "artifact_uri": artifact_uri,
                "lifecycle_stage": "active",
                "run_name": run_name
            },
            "data": {
                "tags": tags or [],
                "params": [],
                "metrics": []
            }
        }

        self._runs[run_id] = run
        return run

    def get_run(self, run_id):
        return self._runs.get(run_id)

    def search_runs(self, experiment_ids):
        results = []
        for run in self._runs.values():
            if run["info"]["experiment_id"] in experiment_ids:
                results.append(run)
        return results

    def list_artifacts(self, run_id, path=""):
        run = self.get_run(run_id)
        if run is None:
            return {"root_uri": "", "files": []}

        artifact_uri = run["info"]["artifact_uri"]
        target_path = os.path.join(artifact_uri, path) if path else artifact_uri

        files = []
        try:
            if os.path.isfile(target_path):
                # If it's a file, read and return it in the file listing
                # with content for local file stores
                with open(target_path, "r") as f:
                    content = f.read()
                files.append({
                    "path": os.path.basename(target_path),
                    "is_dir": False,
                    "file_size": os.path.getsize(target_path),
                    "content": content
                })
            elif os.path.isdir(target_path):
                for entry in os.listdir(target_path):
                    full_path = os.path.join(target_path, entry)
                    files.append({
                        "path": entry,
                        "is_dir": os.path.isdir(full_path),
                        "file_size": os.path.getsize(full_path) if os.path.isfile(full_path) else None
                    })
        except (OSError, PermissionError) as e:
            logger.warning(f"Error listing artifacts at {target_path}: {e}")

        return {"root_uri": artifact_uri, "files": files}

    def get_artifact(self, run_id, path=""):
        run = self.get_run(run_id)
        if run is None:
            return None

        artifact_uri = run["info"]["artifact_uri"]
        target_path = os.path.join(artifact_uri, path) if path else artifact_uri

        try:
            if os.path.isfile(target_path):
                with open(target_path, "r") as f:
                    return f.read()
        except (OSError, PermissionError):
            pass

        return None

    def create_registered_model(self, name, tags=None, description=""):
        if name in self._registered_models:
            raise FileExistsError(f"Registered Model (name={name}) already exists.")

        model = {
            "name": name,
            "creation_timestamp": int(time.time() * 1000),
            "last_updated_timestamp": int(time.time() * 1000),
            "description": description,
            "latest_versions": [],
            "tags": tags or []
        }
        self._registered_models[name] = model
        self._model_versions[name] = []
        return model

    def get_registered_model(self, name):
        return self._registered_models.get(name)

    def create_model_version(self, name, source, run_id="",
                             description="", tags=None):
        if name not in self._registered_models:
            raise FileNotFoundError(f"Registered Model with name={name} not found.")

        resolved_source = _resolve_source_uri(source)

        version_num = len(self._model_versions[name]) + 1

        # Read source artifact metadata if local
        source_content = None
        try:
            if os.path.isfile(resolved_source):
                with open(resolved_source, "r") as f:
                    source_content = f.read()
        except (OSError, PermissionError):
            pass

        model_version = {
            "name": name,
            "version": str(version_num),
            "creation_timestamp": int(time.time() * 1000),
            "last_updated_timestamp": int(time.time() * 1000),
            "current_stage": "None",
            "description": description,
            "source": resolved_source,
            "run_id": run_id,
            "status": "READY",
            "tags": tags or []
        }

        if source_content is not None:
            model_version["source_content"] = source_content

        self._model_versions[name].append(model_version)
        self._registered_models[name]["latest_versions"].append(model_version)
        self._registered_models[name]["last_updated_timestamp"] = int(time.time() * 1000)

        return model_version

    def get_model_version(self, name, version):
        if name not in self._model_versions:
            return None
        for mv in self._model_versions[name]:
            if mv["version"] == str(version):
                return mv
        return None
