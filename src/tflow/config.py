import json
import os
from pathlib import Path
from typing import Dict, Any

def get_global_config_path() -> Path:
    config_dir = Path.home() / ".tflow"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"

def load_global_config() -> Dict[str, Any]:
    path = get_global_config_path()
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_project_config(project_dir: str = ".") -> Dict[str, Any]:
    path = Path(project_dir) / ".tflow.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_config(project_dir: str = ".") -> Dict[str, Any]:
    # Priority: CLI (handled elsewhere) > Project > Global > Defaults
    config = {
        "server_port": 3000,
        "max_budget": 5.0,
    }
    
    global_config = load_global_config()
    project_config = load_project_config(project_dir)
    
    config.update(global_config)
    config.update(project_config)
    
    return config
