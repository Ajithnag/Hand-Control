import json
import os
from typing import Any, Dict

CONFIG_FILENAME = "config.json"

_default_config: Dict[str, Any] = {
    "precision_mode": False,
    "cursor_alpha_default": 0.6,
    "cursor_gain": 1.0,
    "click_mode": "tap",  # default to TAP for non-pinch clicks
}


def get_config_path(project_root: str) -> str:
    return os.path.join(project_root, CONFIG_FILENAME)


def load_config(project_root: str) -> Dict[str, Any]:
    path = get_config_path(project_root)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # merge defaults
                    cfg = {**_default_config, **data}
                    return cfg
        except Exception:
            pass
    return dict(_default_config)


def save_config(project_root: str, cfg: Dict[str, Any]) -> None:
    path = get_config_path(project_root)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        # best-effort; ignore persistence errors
        pass
