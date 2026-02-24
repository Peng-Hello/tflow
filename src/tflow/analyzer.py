import hashlib
import json
from pathlib import Path
from typing import Dict, List, Any

CACHE_VERSION = "1.0"

def calculate_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def scan_project_files(project_dir: Path) -> List[Path]:
    """Scan for frontend source files."""
    extensions = {'.vue', '.tsx', '.ts', '.jsx', '.js', '.svelte'}
    ignored_dirs = {'node_modules', 'dist', 'build', '.git', '.next', '.nuxt'}
    
    source_files = []
    stack = [project_dir]
    
    while stack:
        current_dir = stack.pop()
        try:
            for item in current_dir.iterdir():
                if item.is_dir() and item.name not in ignored_dirs:
                    stack.append(item)
                elif item.is_file() and item.suffix in extensions:
                    source_files.append(item)
        except PermissionError:
            continue
            
    return source_files

def get_cache_path(project_dir: Path) -> Path:
    """Get project cache file path."""
    return project_dir / ".tflow_cache.json"

def load_cache(project_dir: Path) -> Dict[str, Any]:
    """Load analysis cache."""
    cache_path = get_cache_path(project_dir)
    if not cache_path.exists():
        return {"version": CACHE_VERSION, "file_hashes": {}}
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data.get("version") != CACHE_VERSION:
                return {"version": CACHE_VERSION, "file_hashes": {}}
            return data
    except Exception:
        return {"version": CACHE_VERSION, "file_hashes": {}}

def save_cache(project_dir: Path, cache_data: Dict[str, Any]) -> None:
    """Save analysis cache."""
    cache_path = get_cache_path(project_dir)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)

def detect_changed_files(project_dir: Path, source_files: List[Path], cache_data: Dict[str, Any]) -> List[Path]:
    """Detect files that have changed since last analysis."""
    old_hashes = cache_data.get("file_hashes", {})
    changed_files = []
    
    for file_path in source_files:
        rel_path = str(file_path.relative_to(project_dir))
        current_hash = calculate_file_hash(file_path)
        if old_hashes.get(rel_path) != current_hash:
            changed_files.append(file_path)
            
    return changed_files

# Stubs for Claude Agent invocations
def invoke_agent_analysis(files: List[Path]) -> Dict[str, Any]:
    """Invoke Claude Agent for code analysis. (Stub)"""
    return {
        "tech_stack": detect_tech_stack(files),
        "routes": extract_routes(files),
        "api_endpoints": detect_api_endpoints(files),
        "components": identify_components(files),
        "auth_flows": detect_auth_flows(files)
    }

def detect_tech_stack(files: List[Path]) -> str:
    # Stub
    return "Vue 3"

def extract_routes(files: List[Path]) -> List[dict]:
    # Stub
    return []

def detect_api_endpoints(files: List[Path]) -> List[dict]:
    # Stub
    return []

def identify_components(files: List[Path]) -> List[dict]:
    # Stub
    return []

def detect_auth_flows(files: List[Path]) -> List[dict]:
    # Stub
    return []
