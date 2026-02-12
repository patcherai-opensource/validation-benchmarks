"""
LoLLMs Binding Module
Handles dynamic loading and management of AI model bindings
"""
import importlib
import importlib.machinery
import sys
from pathlib import Path


class LLMBinding:
    """Base class for all LLM bindings"""

    binding_type_name = "BaseLLM"

    def __init__(self, config, **kwargs):
        self.config = config
        self.binding_dir = kwargs.get("binding_dir", None)

    def generate(self, prompt, n_predict=128, **kwargs):
        raise NotImplementedError("Subclasses must implement generate()")

    def get_model_info(self):
        return {
            "binding_type": self.binding_type_name,
            "binding_dir": str(self.binding_dir) if self.binding_dir else None,
        }

    @staticmethod
    def list_models():
        return []


class BindingBuilder:
    """Builds and loads binding modules dynamically"""

    def build_binding(self, bindings_path, binding_name, config):
        binding_path = Path(bindings_path) / binding_name
        absolute_path = binding_path.resolve()

        init_file = absolute_path / "__init__.py"
        if not init_file.exists():
            raise FileNotFoundError(
                f"Binding module not found at {init_file}"
            )

        module_name = f"bindings.{binding_name}"
        if module_name in sys.modules:
            del sys.modules[module_name]

        loader = importlib.machinery.SourceFileLoader(
            module_name, str(init_file)
        )
        binding_module = loader.load_module()

        if hasattr(binding_module, "Binding"):
            return binding_module.Binding(config, binding_dir=absolute_path)
        else:
            raise AttributeError(
                f"Binding module {binding_name} does not have a 'Binding' class"
            )
