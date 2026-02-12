"""
Default Binding for LoLLMs
A placeholder binding that echoes inputs when no real model is loaded
"""


class Binding:
    binding_type_name = "default_binding"

    def __init__(self, config, **kwargs):
        self.config = config
        self.binding_dir = kwargs.get("binding_dir", None)

    def generate(self, prompt, n_predict=128, **kwargs):
        return f"[Default Binding] No model loaded. Received prompt: {prompt[:50]}..."

    def on_uninstall(self):
        pass

    @staticmethod
    def list_models():
        return ["echo_model"]
