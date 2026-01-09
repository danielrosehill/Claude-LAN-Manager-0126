"""Terminal launcher for Claude Code with MCP isolation."""

import os
import subprocess
import shutil
from pathlib import Path

from claude_lan_manager.config import AppConfig, Space


def ensure_space_exists(config: AppConfig, space: Space) -> None:
    """Ensure the space directory and required files exist."""
    from claude_lan_manager.config import generate_mcp_json, generate_claude_md
    import json

    # Create directory structure
    space.path.mkdir(parents=True, exist_ok=True)
    space.logs_path.mkdir(exist_ok=True)

    # Get devices for this space
    devices = config.get_devices_for_space(space)

    # Generate CLAUDE.md if it doesn't exist
    if not space.claude_md_path.exists():
        content = generate_claude_md(space, devices)
        space.claude_md_path.write_text(content)

    # Always regenerate .mcp.json to ensure it's current
    mcp_config = generate_mcp_json(devices)
    with open(space.mcp_json_path, "w") as f:
        json.dump(mcp_config, f, indent=2)


def launch_claude_in_terminal(config: AppConfig, space: Space) -> subprocess.Popen:
    """Launch Claude Code in a terminal at the space directory.

    The key here is MCP isolation - we want Claude to ONLY use the MCPs
    defined in the space's .mcp.json, not any user-level MCPs.

    We use --strict-mcp-config with --mcp-config to ensure ONLY the space's
    MCP configuration is used, ignoring user-level and project-level MCPs.
    """
    # Ensure space directory and files exist
    ensure_space_exists(config, space)

    terminal = config.terminal_emulator
    claude_cmd = config.claude_code_cmd
    space_path = space.path
    mcp_json_path = space.mcp_json_path

    # Build environment
    env = os.environ.copy()

    # Build the Claude command with MCP isolation flags
    # --strict-mcp-config: Only use MCP servers from --mcp-config, ignoring all other MCP configurations
    # --mcp-config: Load MCP servers from the space's .mcp.json file
    claude_full_cmd = f'{claude_cmd} --strict-mcp-config --mcp-config "{mcp_json_path}"'

    # Build the command based on terminal emulator
    if terminal == "konsole":
        # Konsole command: open new window, set working directory, run claude
        cmd = [
            "konsole",
            "--new-tab",
            "--workdir", str(space_path),
            "-e", "bash", "-c", claude_full_cmd,
        ]
    elif terminal == "gnome-terminal":
        cmd = [
            "gnome-terminal",
            "--working-directory", str(space_path),
            "--", "bash", "-c", claude_full_cmd,
        ]
    elif terminal == "xterm":
        cmd = [
            "xterm",
            "-e", f"cd {space_path} && {claude_full_cmd}",
        ]
    elif terminal == "kitty":
        cmd = [
            "kitty",
            "--directory", str(space_path),
            "bash", "-c", claude_full_cmd,
        ]
    elif terminal == "alacritty":
        cmd = [
            "alacritty",
            "--working-directory", str(space_path),
            "-e", "bash", "-c", claude_full_cmd,
        ]
    else:
        # Generic fallback - try to use the terminal directly
        cmd = [
            terminal,
            "-e", f"cd {space_path} && {claude_full_cmd}",
        ]

    # Launch the terminal
    process = subprocess.Popen(
        cmd,
        env=env,
        start_new_session=True,  # Detach from parent process
    )

    return process


def check_terminal_available(terminal: str) -> bool:
    """Check if the specified terminal emulator is available."""
    return shutil.which(terminal) is not None


def check_claude_available(claude_cmd: str) -> bool:
    """Check if Claude Code is available."""
    return shutil.which(claude_cmd) is not None
