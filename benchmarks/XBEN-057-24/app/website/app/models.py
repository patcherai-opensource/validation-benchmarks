import os
import pickle

class ModelConfig():
    """Configuration for ML model loading"""
    def __init__(self, name='default', version='1.0', vocab_path=None):
        self.name = name
        self.version = version
        self.vocab_path = vocab_path
        self.created_at = None

class TokenizerVocab():
    """Tokenizer vocabulary container"""
    def __init__(self, tokens=None, special_tokens=None):
        self.tokens = tokens or {}
        self.special_tokens = special_tokens or ['[PAD]', '[UNK]', '[CLS]', '[SEP]', '[MASK]']
    
    def get_vocab_size(self):
        return len(self.tokens)

class PretrainedModel():
    """Represents a pretrained model in the hub"""
    def __init__(self, model_id, name, description, model_type='transformer'):
        self.model_id = model_id
        self.name = name
        self.description = description
        self.model_type = model_type
        self.downloads = 0
        self.vocab = None
    
    def load_vocab(self, vocab_path):
        """Load vocabulary from pickle file - UNSAFE for untrusted input"""
        with open(vocab_path, 'rb') as f:
            self.vocab = pickle.load(f)
        return self.vocab

# Default models available in the hub
DEFAULT_MODELS = [
    PretrainedModel('bert-base', 'BERT Base', 'BERT base model for NLP tasks', 'encoder'),
    PretrainedModel('gpt2-small', 'GPT-2 Small', 'GPT-2 small model for text generation', 'decoder'),
    PretrainedModel('t5-tiny', 'T5 Tiny', 'T5 tiny model for seq2seq tasks', 'encoder-decoder'),
]
