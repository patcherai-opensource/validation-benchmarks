import json
import os
import time


class ExperimentRun:
    def __init__(self, exp_id, name, status='pending', metric='accuracy',
                 best_score=None, model_type='generic', dataset='unknown',
                 num_epochs=10, created_at=None):
        self.id = exp_id
        self.name = name
        self.status = status
        self.metric = metric
        self.best_score = best_score
        self.model_type = model_type
        self.dataset = dataset
        self.num_epochs = num_epochs
        self.created_at = created_at or time.strftime('%Y-%m-%dT%H:%M:%SZ')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'metric': self.metric,
            'best_score': self.best_score,
            'model_type': self.model_type,
            'dataset': self.dataset,
            'num_epochs': self.num_epochs,
            'created_at': self.created_at,
        }


class CheckpointRecord:
    def __init__(self, path, score, epoch=None):
        self.path = path
        self.score = score
        self.epoch = epoch

    def to_dict(self):
        return {
            'path': self.path,
            'score': self.score,
            'epoch': self.epoch,
        }


def load_experiments(db_path):
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            return json.load(f)
    return []


def save_experiments(db_path, experiments):
    with open(db_path, 'w') as f:
        json.dump(experiments, f, indent=2)
