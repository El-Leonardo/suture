import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger("suture-mcp")

CONFIG_FILE = Path(os.getcwd()) / ".suture_config.json"

DEFAULT_CONFIG = {
    "phases": ["Plan", "Work", "Test", "Git Commit"],
    "linters": [
        {
            "name": "Black Formatter",
            "command": ["black", "--check", "{path}"],
            "success_message": "Black check passed: Code is properly formatted."
        },
        {
            "name": "Flake8 Linter",
            "command": ["flake8", "{path}"],
            "success_message": "Flake8 check passed: No linting errors found."
        }
    ]
}

def load_config() -> Dict[str, Any]:
    """Load Suture configuration from .suture_config.json, or return defaults."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r") as f:
            user_config = json.load(f)
            # Merge user config with defaults
            config = DEFAULT_CONFIG.copy()
            if "phases" in user_config:
                config["phases"] = user_config["phases"]
            if "linters" in user_config:
                config["linters"] = user_config["linters"]
            return config
    except Exception as e:
        logger.error(f"Failed to load config from {CONFIG_FILE}: {e}")
        return DEFAULT_CONFIG
