import logging
import subprocess
from typing import List, Optional
import os
import re

from mcp.server.fastmcp import FastMCP
from suture.config import load_config

logger = logging.getLogger("suture-mcp")

def register_quality_tools(mcp: FastMCP) -> None:
    """Register quality and safety tools with the FastMCP instance."""

    @mcp.tool()
    def lint(path: str = ".") -> str:
        """Run configured code quality checks on a given path.

        Args:
            path: The file or directory path to lint. Defaults to current directory.

        Returns:
            The output of the configured linters.
        """
        output = []
        config = load_config()
        linters = config.get("linters", [])

        if not linters:
            return "No linters configured."

        for linter in linters:
            name = linter.get("name", "Unknown Linter")
            command = linter.get("command", [])
            success_message = linter.get("success_message", f"{name} check passed.")

            output.append(f"=== {name} Check ===")

            if not command:
                output.append(f"Error: No command specified for {name}.")
                output.append("")
                continue

            # Format the command with the path
            formatted_command = [arg.replace("{path}", path) for arg in command]

            try:
                result = subprocess.run(
                    formatted_command,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    output.append(success_message)
                else:
                    output.append(f"{name} check failed:")
                    output.append(result.stderr.strip() or result.stdout.strip())
            except Exception as e:
                output.append(f"Failed to run {name}: {e}")

            output.append("")

        return "\n".join(output).strip()

    @mcp.tool()
    def safety_check(path: str = ".") -> str:
        """Scan a given file or directory for potentially leaked secrets and API keys.

        Args:
            path: The file or directory path to scan. Defaults to current directory.

        Returns:
            A report of any potential secrets found.
        """
        # Basic regex patterns for common secrets
        patterns = {
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "GitHub Token": r"(gh[pousr]_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59})",
            "Generic API Key": r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)[\s:=]+[\"']?[A-Za-z0-9\-_]{16,}[\"']?",
            "RSA Private Key": r"-----BEGIN RSA PRIVATE KEY-----",
        }

        findings = []

        # Walk the directory
        target_path = os.path.abspath(path)
        if os.path.isfile(target_path):
            files_to_check = [target_path]
        else:
            files_to_check = []
            for root, _, files in os.walk(target_path):
                # Skip common ignore dirs
                if any(ignored in root for ignored in [".git", "__pycache__", "venv", "node_modules"]):
                    continue
                for file in files:
                    files_to_check.append(os.path.join(root, file))

        for file_path in files_to_check:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for name, pattern in patterns.items():
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            # Context window
                            start = max(0, match.start() - 20)
                            end = min(len(content), match.end() + 20)
                            snippet = content[start:end].replace('\n', ' ')
                            findings.append(f"[{name}] found in {os.path.relpath(file_path, start=target_path)}: ...{snippet}...")
            except Exception as e:
                logger.debug(f"Could not read {file_path} for safety check: {e}")

        if findings:
            return "⚠️ SAFETY CHECK FAILED: Potential secrets found!\n\n" + "\n".join(findings)

        return "✅ Safety check passed. No obvious secrets detected."

    @mcp.tool()
    def verify_plan(plan_content: str) -> str:
        """Verify that a markdown plan follows configured Suture phases.

        This ensures the plan explicitly contains required phases before work begins.

        Args:
            plan_content: The markdown string containing the proposed plan.

        Returns:
            A verification report indicating if the plan meets constraints.
        """
        config = load_config()
        required_keywords = config["phases"]
        missing = []

        plan_lower = plan_content.lower()
        for kw in required_keywords:
            if kw.lower() not in plan_lower:
                missing.append(kw)

        if missing:
            return f"❌ Plan Verification Failed. The plan is missing required configured phases: {', '.join(missing)}.\nPlease update the plan to include these phases."

        return "✅ Plan Verification Passed. All required phases are present."
