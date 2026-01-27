
class ModelConfig():
    """Represents a model configuration with vocabulary"""
    def __init__(self, name='model', vocab_size=30522, hidden_size=768):
        self.name = name
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
    
    def __repr__(self):
        return f"ModelConfig(name={self.name}, vocab_size={self.vocab_size})"


class VocabEntry():
    """Represents a vocabulary entry"""
    def __init__(self, token, token_id):
        self.token = token
        self.token_id = token_id
