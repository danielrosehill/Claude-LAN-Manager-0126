"""Configuration management for Claude LAN Manager."""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import yaml
from dotenv import load_dotenv


@dataclass
class Device:
    """Represents a network device with MCP endpoint."""
    id: str
    name: str
    ip: str
    mcp_port: int
    description: str = ""
    category: str = "individual"  # "individual", "group", "consolidated"
    icon: str = "computer"  # Icon hint for GUI

    @property
    def mcp_url(self) -> str:
        """Generate the MCP endpoint URL."""
        return f"http://{self.ip}:{self.mcp_port}/mcp"


@dataclass
class Space:
    """Represents a Claude Space configuration."""
    id: str
    name: str
    path: Path
    devices: list[str]  # List of device IDs
    category: str = "individual"
    description: str = ""

    @property
    def claude_md_path(self) -> Path:
        return self.path / "CLAUDE.md"

    @property
    def mcp_json_path(self) -> Path:
        return self.path / ".mcp.json"

    @property
    def logs_path(self) -> Path:
        return self.path / "logs"

    def exists(self) -> bool:
        return self.path.exists()


@dataclass
class AppConfig:
    """Application configuration."""
    spaces_base_path: Path
    terminal_emulator: str = "konsole"
    claude_code_cmd: str = "claude"
    devices: dict[str, Device] = field(default_factory=dict)
    spaces: dict[str, Space] = field(default_factory=dict)

    @classmethod
    def get_default_spaces_path(cls) -> Path:
        """Get the default path for Claude Spaces data."""
        # Default to ~/.local/share/claude-lan-manager/spaces
        xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        return Path(xdg_data) / "claude-lan-manager" / "spaces"

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "AppConfig":
        """Load configuration from file."""
        # Try to find config file
        if config_path is None:
            # Check common locations
            candidates = [
                Path.cwd() / "config" / "config.yaml",
                Path.cwd() / "config.yaml",
                Path.home() / ".config" / "claude-lan-manager" / "config.yaml",
            ]
            for candidate in candidates:
                if candidate.exists():
                    config_path = candidate
                    break

        # Load environment variables
        load_dotenv()

        # Start with defaults
        spaces_path = Path(os.environ.get(
            "CLAUDE_SPACES_PATH",
            cls.get_default_spaces_path()
        ))

        config = cls(
            spaces_base_path=spaces_path,
            terminal_emulator=os.environ.get("TERMINAL_EMULATOR", "konsole"),
            claude_code_cmd=os.environ.get("CLAUDE_CODE_CMD", "claude"),
        )

        # Load from YAML if exists
        if config_path and config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}

            if "spaces_base_path" in data:
                config.spaces_base_path = Path(os.path.expanduser(data["spaces_base_path"]))
            if "terminal_emulator" in data:
                config.terminal_emulator = data["terminal_emulator"]
            if "claude_code_cmd" in data:
                config.claude_code_cmd = data["claude_code_cmd"]

            # Load devices
            for dev_data in data.get("devices", []):
                device = Device(
                    id=dev_data["id"],
                    name=dev_data["name"],
                    ip=dev_data["ip"],
                    mcp_port=dev_data["mcp_port"],
                    description=dev_data.get("description", ""),
                    category=dev_data.get("category", "individual"),
                    icon=dev_data.get("icon", "computer"),
                )
                config.devices[device.id] = device

            # Load spaces
            for space_data in data.get("spaces", []):
                space = Space(
                    id=space_data["id"],
                    name=space_data["name"],
                    path=config.spaces_base_path / space_data["id"],
                    devices=space_data.get("devices", []),
                    category=space_data.get("category", "individual"),
                    description=space_data.get("description", ""),
                )
                config.spaces[space.id] = space

        return config

    def save(self, config_path: Path) -> None:
        """Save configuration to file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "spaces_base_path": str(self.spaces_base_path),
            "terminal_emulator": self.terminal_emulator,
            "claude_code_cmd": self.claude_code_cmd,
            "devices": [
                {
                    "id": d.id,
                    "name": d.name,
                    "ip": d.ip,
                    "mcp_port": d.mcp_port,
                    "description": d.description,
                    "category": d.category,
                    "icon": d.icon,
                }
                for d in self.devices.values()
            ],
            "spaces": [
                {
                    "id": s.id,
                    "name": s.name,
                    "devices": s.devices,
                    "category": s.category,
                    "description": s.description,
                }
                for s in self.spaces.values()
            ],
        }

        with open(config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def get_devices_for_space(self, space: Space) -> list[Device]:
        """Get all Device objects for a space."""
        return [self.devices[dev_id] for dev_id in space.devices if dev_id in self.devices]


def generate_mcp_json(devices: list[Device]) -> dict:
    """Generate mcp.json content for given devices.

    This creates a configuration that ONLY includes the specified MCPs,
    ensuring no user-level MCPs bleed through.

    Note: Claude Code uses "type": "http" for Streamable HTTP transport,
    not "streamableHttp" which is the MCP protocol terminology.
    """
    mcp_servers = {}

    for device in devices:
        server_name = f"{device.id}-mcp"
        mcp_servers[server_name] = {
            "type": "http",
            "url": device.mcp_url,
        }

    return {"mcpServers": mcp_servers}


def generate_claude_md(space: Space, devices: list[Device]) -> str:
    """Generate CLAUDE.md content for a space."""
    device_list = "\n".join([
        f"- **{d.name}** ({d.ip}:{d.mcp_port}): {d.description}"
        for d in devices
    ])

    if space.category == "consolidated":
        role = "LAN Manager"
        role_desc = "You are the consolidated LAN Manager for the home network."
    elif space.category == "group":
        role = f"{space.name}"
        role_desc = f"You are the {space.name}, responsible for managing a group of related devices."
    else:
        device_name = devices[0].name if devices else "Unknown Device"
        role = f"{device_name} Manager"
        role_desc = f"You are the dedicated manager for {device_name}."

    return f"""# {role}

{role_desc}

## Your Role

You are a systems administration assistant. Your task is to help the user manage and administer the device(s) under your control using the MCP tools available to you.

## Managed Devices

{device_list}

## Available Tools

You have MCP connections to the device(s) listed above. Use these tools to:
- Execute commands on the target system(s)
- Read and write files
- Check system status
- Perform administrative tasks

## Guidelines

1. **Be careful with destructive operations** - Always confirm before deleting files or making irreversible changes
2. **Log important actions** - Save notes and logs to the `logs/` subfolder
3. **Stay focused** - Only interact with the devices assigned to you
4. **Report issues** - If you encounter connectivity problems or errors, inform the user

## Logging

Save any important logs, notes, or documentation to the `logs/` subfolder in this space:
- `logs/session-YYYY-MM-DD.md` for session notes
- `logs/changes.md` for tracking configuration changes
- `logs/issues.md` for recording problems and resolutions

## Network Context

All devices are on the local network (10.0.0.0/24). MCP servers use Streamable HTTP transport and are unauthenticated (local network only).
"""
