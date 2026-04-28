import os
import signal
import subprocess
import threading
from pathlib import Path
from typing import Any, Iterator

import yaml


APPS_DIR = Path(__file__).resolve().parents[2]
MODULE_FILE = "module.yml"
RESTART_DELAY_SECONDS = 2.0


class LocalAppsManager:
    def __init__(self, apps_dir: Path = APPS_DIR):
        self.apps_dir = apps_dir

    def enable(self, name: str, restart: bool = True) -> dict[str, Any]:
        return self._set_enabled_by_name(name=name, enabled=True, restart=restart)

    def disable(self, name: str, restart: bool = True) -> dict[str, Any]:
        return self._set_enabled_by_name(name=name, enabled=False, restart=restart)

    def restart_fastapi(self):
        timer = threading.Timer(RESTART_DELAY_SECONDS, self._terminate_fastapi_process)
        timer.daemon = True
        timer.start()

    def _iter_configs(self) -> Iterator[tuple[Path, dict[str, Any]]]:
        for app_dir in sorted(self.apps_dir.iterdir(), key=lambda path: path.name):
            if not app_dir.is_dir():
                continue

            config = self._read_config(app_dir)
            if config is None:
                continue

            yield app_dir, config

    def _read_config(self, app_dir: Path) -> dict[str, Any] | None:
        module_file = app_dir / MODULE_FILE
        if not module_file.exists():
            return None

        with module_file.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        if not isinstance(config, dict):
            return {}

        return config

    def _write_config(self, app_dir: Path, config: dict[str, Any]):
        module_file = app_dir / MODULE_FILE
        with module_file.open("w", encoding="utf-8") as file:
            yaml.safe_dump(config, file, allow_unicode=True, sort_keys=False)

    def response(self) -> list[dict[str, Any]]:
        return [config for _, config in self._iter_configs()]

    def _set_enabled_by_name(self, name: str, enabled: bool, restart: bool) -> dict[str, Any]:
        app_dir, config = self._find_config_by_name(name)
        config["enabled"] = enabled
        self._write_config(app_dir, config)

        restart_info = {"scheduled": False, "delay": 0}
        if restart:
            self.restart_fastapi()
            restart_info = {"scheduled": True, "delay": RESTART_DELAY_SECONDS}

        return {
            "updated": config,
            "restart": restart_info,
            "state": self.response(),
        }

    def _find_config_by_name(self, name: str) -> tuple[Path, dict[str, Any]]:
        for app_dir, config in self._iter_configs():
            if config.get("name") == name:
                return app_dir, config

        raise FileNotFoundError(name)

    def _terminate_fastapi_process(self):
        target_pid = os.getpid()
        parent_pid = os.getppid()
        if self._is_uvicorn_process(parent_pid):
            target_pid = parent_pid

        try:
            os.kill(target_pid, signal.SIGTERM)
        except ProcessLookupError:
            os.kill(os.getpid(), signal.SIGTERM)

    def _is_uvicorn_process(self, pid: int) -> bool:
        try:
            command = subprocess.check_output(
                ["ps", "-p", str(pid), "-o", "command="],
                text=True,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            return False

        return "uvicorn" in command.lower()
