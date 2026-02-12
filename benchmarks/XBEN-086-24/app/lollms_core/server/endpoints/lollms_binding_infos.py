"""
LoLLMs Binding Information Endpoints
Handles binding installation, removal, and information queries
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil
import logging

from lollms_core.config import LOLLMsConfig
from lollms_core.binding import BindingBuilder

logger = logging.getLogger(__name__)
router = APIRouter()


class BindingInstallParams(BaseModel):
    name: str


class BindingInfoParams(BaseModel):
    name: str


@router.get("/list_bindings")
async def list_bindings():
    """List all available bindings"""
    config = LOLLMsConfig()
    bindings_path = config.bindings_path
    bindings = []

    if bindings_path.exists():
        for item in bindings_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                bindings.append({
                    "name": item.name,
                    "path": str(item),
                    "installed": True,
                })

    return {"bindings": bindings}


@router.post("/get_binding_infos")
async def get_binding_infos(data: BindingInfoParams):
    """Get detailed information about a specific binding"""
    config = LOLLMsConfig()
    binding_path = config.bindings_path / data.name

    if not binding_path.exists():
        raise HTTPException(status_code=404, detail="Binding not found")

    info = {
        "name": data.name,
        "path": str(binding_path),
        "has_init": (binding_path / "__init__.py").exists(),
        "files": [f.name for f in binding_path.iterdir()] if binding_path.exists() else [],
    }
    return info


@router.post("/install_binding")
async def install_binding(data: BindingInstallParams):
    """Install a new binding"""
    config = LOLLMsConfig()
    binding_path = config.bindings_path / data.name

    if binding_path.exists():
        raise HTTPException(status_code=400, detail="Binding already exists")

    binding_path.mkdir(parents=True, exist_ok=True)

    init_content = '''"""
{name} binding placeholder
"""

class Binding:
    binding_type_name = "{name}"

    def __init__(self, config, **kwargs):
        self.config = config
        self.binding_dir = kwargs.get("binding_dir", None)

    def generate(self, prompt, n_predict=128, **kwargs):
        return "Binding {name} is not yet configured with a model."

    @staticmethod
    def list_models():
        return []
'''.format(name=data.name)

    with open(binding_path / "__init__.py", "w") as f:
        f.write(init_content)

    return {"status": True, "message": f"Binding {data.name} installed successfully"}


@router.post("/unInstall_binding")
async def uninstall_binding(data: BindingInstallParams):
    """Uninstall a binding by name"""
    config = LOLLMsConfig()

    # Store current binding name
    old_binding = config.binding_name

    # Set binding name to the one being uninstalled so we can properly clean up
    config.binding_name = data.name

    try:
        # Attempt to load the binding to run any cleanup hooks
        builder = BindingBuilder()
        try:
            binding = builder.build_binding(
                config.bindings_path, config.binding_name, config
            )
            if hasattr(binding, "on_uninstall"):
                binding.on_uninstall()
            logger.info(f"Ran cleanup hooks for binding: {data.name}")
        except Exception as e:
            logger.warning(f"Could not load binding for cleanup: {e}")

        # Remove the binding directory
        binding_path = config.bindings_path / data.name
        if binding_path.exists() and binding_path.is_dir():
            shutil.rmtree(binding_path, ignore_errors=True)
            logger.info(f"Removed binding directory: {binding_path}")

        # Restore to default binding
        config.binding_name = "default_binding"
        config.save()

        return {"status": True, "message": f"Binding {data.name} uninstalled successfully"}
    except Exception as e:
        # Restore old binding name on failure
        config.binding_name = old_binding
        logger.error(f"Error uninstalling binding: {e}")
        raise HTTPException(status_code=500, detail=str(e))
