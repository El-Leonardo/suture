import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import os

from mcp.server.fastmcp import FastMCP
from suture.config import load_config

logger = logging.getLogger("suture-mcp")

def register_loop_tools(mcp: FastMCP) -> None:
    """Register loop and workflow tools with the FastMCP instance."""

    # Workflow tracking file
    WORKFLOW_FILE = Path(os.getcwd()) / ".suture_workflow.json"

    def _load_workflow() -> Dict[str, Any]:
        if not WORKFLOW_FILE.exists():
            return {"current_phase": None, "loop_active": False, "loop_goal": None, "iterations": []}
        try:
            with open(WORKFLOW_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load workflow from {WORKFLOW_FILE}: {e}")
            return {"current_phase": None, "loop_active": False, "loop_goal": None, "iterations": []}

    def _save_workflow(data: Dict[str, Any]) -> None:
        try:
            with open(WORKFLOW_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save workflow to {WORKFLOW_FILE}: {e}")

    @mcp.tool()
    def start_loop(goal: str) -> str:
        """Start an automated multi-agent loop with a specific goal.

        Args:
            goal: The overarching goal of the loop to be achieved.

        Returns:
            A status message indicating the loop has started.
        """
        data = _load_workflow()
        if data.get("loop_active"):
            return "A loop is already active. Please finish the current loop before starting a new one."

        data["loop_active"] = True
        data["loop_goal"] = goal
        data["iterations"] = []
        _save_workflow(data)
        return f"Loop started successfully with goal: '{goal}'. Use record_loop_iteration to document progress."

    @mcp.tool()
    def record_loop_iteration(notes: str) -> str:
        """Record the progress and findings of a single loop iteration.

        This prevents hallucinations by forcing the agent to document what worked
        and what didn't during the loop.

        Args:
            notes: What happened during this iteration (successes, failures, learned facts).

        Returns:
            A status message indicating the iteration was recorded.
        """
        data = _load_workflow()
        if not data.get("loop_active"):
            return "No loop is currently active. Use start_loop first."

        iteration_num = len(data.get("iterations", [])) + 1
        data["iterations"].append({
            "iteration": iteration_num,
            "notes": notes
        })
        _save_workflow(data)
        return f"Iteration {iteration_num} recorded successfully."

    @mcp.tool()
    def finish_loop(final_result: str) -> str:
        """Finish the currently active automated loop and save it to history.

        Args:
            final_result: The final outcome or result of the loop.

        Returns:
            A summary of the loop completion.
        """
        data = _load_workflow()
        if not data.get("loop_active"):
            return "No loop is currently active to finish."

        total_iterations = len(data.get("iterations", []))
        goal = data.get("loop_goal", "Unknown")
        iterations = data.get("iterations", [])

        # Save loop to history
        HISTORY_FILE = Path(os.getcwd()) / ".suture_history.jsonl"
        history_entry = {
            "goal": goal,
            "final_result": final_result,
            "iterations": iterations
        }

        try:
            with open(HISTORY_FILE, "a") as f:
                f.write(json.dumps(history_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to append to history file {HISTORY_FILE}: {e}")

        # Reset loop state
        data["loop_active"] = False
        data["loop_goal"] = None
        data["iterations"] = []
        _save_workflow(data)

        return f"Loop finished successfully. Goal: '{goal}'. Total iterations: {total_iterations}. Final Result: '{final_result}'. History saved to {HISTORY_FILE.name}."

    @mcp.tool()
    def set_workflow_phase(phase: str) -> str:
        """Set the current workflow phase.

        This is used to strictly enforce the configured workflow phases.

        Args:
            phase: The name of the phase to enter.

        Returns:
            A message confirming the phase change.
        """
        config = load_config()
        allowed_phases = config["phases"]
        if phase not in allowed_phases:
            return f"Warning: '{phase}' is not a standard configured phase. Configured phases are: {', '.join(allowed_phases)}. Phase set anyway."

        data = _load_workflow()
        data["current_phase"] = phase
        _save_workflow(data)
        return f"Workflow phase successfully set to '{phase}'."

    @mcp.tool()
    def get_workflow_status() -> str:
        """Get the current workflow phase and loop status.

        Returns:
            A JSON string representing the current workflow status.
        """
        data = _load_workflow()
        return json.dumps(data, indent=2)
