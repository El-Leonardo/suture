import logging
import subprocess
from typing import List, Optional
import os
import re

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("suture-mcp")


def register_quality_tools(mcp: FastMCP) -> None:
    """Register quality and safety tools with the FastMCP instance."""

    @mcp.tool()
    def lint(path: str = ".") -> str:
        """Run standard enterprise code quality checks (Black and Flake8) on a given path.

        Args:
            path: The file or directory path to lint. Defaults to current directory.

        Returns:
            The output of the linters.
        """
        output = []

        # Run Black
        try:
            black_result = subprocess.run(
                ["black", "--check", path],
                capture_output=True,
                text=True,
            )
            output.append("=== Black Formatter Check ===")
            if black_result.returncode == 0:
                output.append("Black check passed: Code is properly formatted.")
            else:
                output.append("Black check failed:")
                output.append(
                    black_result.stderr.strip() or black_result.stdout.strip()
                )
        except Exception as e:
            output.append(f"Failed to run Black: {e}")

        output.append("")

        # Run Flake8
        try:
            flake8_result = subprocess.run(
                ["flake8", path],
                capture_output=True,
                text=True,
            )
            output.append("=== Flake8 Linter Check ===")
            if flake8_result.returncode == 0:
                output.append("Flake8 check passed: No linting errors found.")
            else:
                output.append("Flake8 check failed:")
                output.append(flake8_result.stdout.strip())
        except Exception as e:
            output.append(f"Failed to run Flake8: {e}")

        return "\n".join(output)

    @mcp.tool()
    def safety_check(path: str = ".") -> str:
        """Scan a given file or directory for potentially leaked secrets and API keys.

        Args:
            path: The file or directory path to scan. Defaults to current directory.

        Returns:
            A report of any potential secrets found.
        """
        # ⚡ Bolt: Pre-compile regex patterns outside the loop for O(1) matching overhead
        # rather than recompiling them for every file checked.
        patterns = {
            "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
            "GitHub Token": re.compile(
                r"(gh[pousr]_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59})"
            ),
            "Generic API Key": re.compile(
                r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)[\s:=]+[\"']?[A-Za-z0-9\-_]{16,}[\"']?"
            ),
            "RSA Private Key": re.compile(r"-----BEGIN RSA PRIVATE KEY-----"),
        }

        findings = []

        # Walk the directory
        target_path = os.path.abspath(path)
        if os.path.isfile(target_path):
            files_to_check = [target_path]
        else:
            files_to_check = []
            # ⚡ Bolt: Prune directories in-place during os.walk to prevent unnecessary disk I/O
            # into large ignored directories (like node_modules or .git).
            ignored_dirs = {".git", "__pycache__", "venv", "node_modules"}
            for root, dirs, files in os.walk(target_path):
                # Modify dirs in-place to prune the walk tree
                dirs[:] = [d for d in dirs if d not in ignored_dirs]

                for file in files:
                    files_to_check.append(os.path.join(root, file))

        for file_path in files_to_check:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for name, pattern in patterns.items():
                        matches = pattern.finditer(content)
                        for match in matches:
                            # Context window
                            start = max(0, match.start() - 20)
                            end = min(len(content), match.end() + 20)
                            snippet = content[start:end].replace("\n", " ")
                            findings.append(
                                f"[{name}] found in {os.path.relpath(file_path, start=target_path)}: ...{snippet}..."
                            )
            except Exception as e:
                logger.debug(f"Could not read {file_path} for safety check: {e}")

        if findings:
            return "⚠️ SAFETY CHECK FAILED: Potential secrets found!\n\n" + "\n".join(
                findings
            )

        return "✅ Safety check passed. No obvious secrets detected."

    @mcp.tool()
    def verify_plan(plan_content: str) -> str:
        """Verify that a markdown plan follows Suture enterprise constraints.

        This ensures the plan explicitly contains required phases before work begins.

        Args:
            plan_content: The markdown string containing the proposed plan.

        Returns:
            A verification report indicating if the plan meets constraints.
        """
        # ⚡ Bolt: Pre-lower case required keywords to avoid doing it inside the loop
        required_keywords_lower = {
            "plan": "Plan",
            "work": "Work",
            "test": "Test",
            "git commit": "Git Commit",
        }
        missing = []

        plan_lower = plan_content.lower()
        for kw_lower, kw_original in required_keywords_lower.items():
            if kw_lower not in plan_lower:
                missing.append(kw_original)

        if missing:
            return f"❌ Plan Verification Failed. The plan is missing required enterprise phases: {', '.join(missing)}.\nPlease update the plan to include these phases."

        return "✅ Plan Verification Passed. All required phases are present."
