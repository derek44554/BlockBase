import sys
from importlib import import_module
from pathlib import Path

import yaml
from blocklink.models.routers.route_block_app import RouteApp


APPS_DIR = Path(__file__).resolve().parent.parent / "apps"
MODULE_FILE = "module.yml"


def is_enabled_app(app_dir: Path) -> bool:
    module_file = app_dir / MODULE_FILE

    if not module_file.exists():
        return False

    with module_file.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    return config.get("enabled") is True


def load_apps() -> list[RouteApp]:
    import_root = str(APPS_DIR.parent)
    if import_root not in sys.path:
        sys.path.insert(0, import_root)

    route_apps: list[RouteApp] = []
    for app_dir in sorted(APPS_DIR.iterdir(), key=lambda path: path.name):
        if not app_dir.is_dir() or not is_enabled_app(app_dir):
            continue

        module = import_module(f"apps.{app_dir.name}")
        route_app = getattr(module, "route_app", None)
        if route_app is None:
            continue

        if not isinstance(route_app, RouteApp):
            raise RuntimeError(f"apps/{app_dir.name}/__init__.py must define route_app.")

        route_apps.append(route_app)

    return route_apps
