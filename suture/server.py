import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# Initialize logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("suture-mcp")

# Create the MCP server instance
mcp = FastMCP("suture-mcp")

# Memory framework file
MEMORY_FILE = Path(os.getcwd()) / ".suture_memory.json"

def _load_memory() -> Dict[str, Any]:
    """Load the memory file from disk."""
    if not MEMORY_FILE.exists():
        return {}
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load memory from {MEMORY_FILE}: {e}")
        return {}

def _save_memory(memory_data: Dict[str, Any]) -> None:
    """Save the memory file to disk."""
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory_data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save memory to {MEMORY_FILE}: {e}")

@mcp.tool()
def store_memory(key: str, value: str) -> str:
    """Store context, facts, or instructions into persistent memory.

    This is useful for preventing hallucination across long loops or sessions.

    Args:
        key: The key under which to store the memory.
        value: The string value to store.

    Returns:
        A success message indicating the memory was stored.
    """
    memory_data = _load_memory()
    memory_data[key] = value
    _save_memory(memory_data)
    return f"Memory stored successfully under key '{key}'."

@mcp.tool()
def retrieve_memory(key: str) -> str:
    """Retrieve previously stored context or facts from persistent memory.

    Args:
        key: The key to retrieve.

    Returns:
        The stored value, or an error message if the key is not found.
    """
    memory_data = _load_memory()
    if key in memory_data:
        return memory_data[key]
    return f"Error: Key '{key}' not found in memory."

@mcp.tool()
def list_memory_keys() -> str:
    """List all keys currently stored in persistent memory.

    Returns:
        A comma-separated list of stored memory keys, or a message if empty.
    """
    memory_data = _load_memory()
    if not memory_data:
        return "Memory is currently empty."
    return "Stored memory keys: " + ", ".join(memory_data.keys())

from suture.loops import register_loop_tools
from suture.quality import register_quality_tools

def main() -> None:
    """Run the Suture MCP Server."""
    logger.info("Starting Suture MCP Server...")
    # Register loop and workflow tools
    register_loop_tools(mcp)
    # Register quality and safety tools
    register_quality_tools(mcp)

    mcp.run()

if __name__ == "__main__":
    main()
