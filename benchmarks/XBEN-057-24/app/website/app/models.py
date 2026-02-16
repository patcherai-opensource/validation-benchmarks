import uuid
import time
import pickle
import json


class DocumentRecord:
    """Represents a stored document with its metadata."""
    def __init__(self, doc_id, content, metadata=None):
        self.doc_id = doc_id
        self.content = content
        self.metadata = metadata or {}
        self.created_at = time.time()

    def to_dict(self):
        return {
            "doc_id": self.doc_id,
            "content": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


class InMemoryDocStore:
    """Simple in-memory document store."""
    def __init__(self):
        self._store = {}

    def add(self, doc_id, document):
        self._store[doc_id] = document

    def search(self, doc_id):
        return self._store.get(doc_id)

    def delete(self, doc_id):
        if doc_id in self._store:
            del self._store[doc_id]
            return True
        return False

    @property
    def count(self):
        return len(self._store)

    def list_all(self):
        return list(self._store.values())


class VectorIndex:
    """Represents a serializable vector index with document store."""
    def __init__(self, name, dimension=128, distance_metric="cosine"):
        self.index_id = uuid.uuid4().hex[:12]
        self.name = name
        self.dimension = dimension
        self.distance_metric = distance_metric
        self.docstore = InMemoryDocStore()
        self.id_mapping = {}
        self.created_at = time.time()
        self.version = "1.0"

    def add_documents(self, documents):
        for doc in documents:
            doc_id = uuid.uuid4().hex[:8]
            record = DocumentRecord(doc_id, doc.get("content", ""), doc.get("metadata", {}))
            self.docstore.add(doc_id, record)
            self.id_mapping[len(self.id_mapping)] = doc_id

    def serialize_to_bytes(self):
        """Serialize the index to bytes."""
        return pickle.dumps((self.name, self.docstore, self.id_mapping, {
            "dimension": self.dimension,
            "distance_metric": self.distance_metric,
            "index_id": self.index_id,
            "version": self.version,
            "created_at": self.created_at,
        }))

    @classmethod
    def restore_from_bytes(cls, serialized):
        """Restore a vector index from serialized bytes."""
        name, docstore, id_mapping, config = pickle.loads(serialized)
        instance = cls.__new__(cls)
        instance.name = name
        instance.docstore = docstore
        instance.id_mapping = id_mapping
        instance.dimension = config.get("dimension", 128)
        instance.distance_metric = config.get("distance_metric", "cosine")
        instance.index_id = config.get("index_id", uuid.uuid4().hex[:12])
        instance.version = config.get("version", "1.0")
        instance.created_at = config.get("created_at", time.time())
        return instance

    def info(self):
        return {
            "index_id": self.index_id,
            "name": self.name,
            "dimension": self.dimension,
            "distance_metric": self.distance_metric,
            "document_count": self.docstore.count,
            "version": self.version,
            "created_at": self.created_at,
        }
