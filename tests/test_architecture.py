import ast
from pathlib import Path

from flower_shop.service import health


def test_service_layer_does_not_depend_on_transport_config_or_storage():
    forbidden = {"fastapi", "starlette", "httpx", "requests", "pydantic", "config", "repository"}
    folder = Path(health.__file__).parent

    for module in folder.rglob("*.py"):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imports = [node.module or ""]
                if not node.module:
                    imports.extend(alias.name for alias in node.names)
            else:
                continue
            for imported in imports:
                assert forbidden.isdisjoint(imported.split(".")), (
                    f"Service layer {module.name} imports {imported}; "
                    "keep HTTP, configuration and storage details in outer layers"
                )
