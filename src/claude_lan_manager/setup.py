"""Setup utilities for Claude LAN Manager."""

import shutil
from pathlib import Path

from claude_lan_manager.config import AppConfig, generate_mcp_json, generate_claude_md


def initialize_spaces(config: AppConfig, force: bool = False) -> list[str]:
    """Initialize all configured spaces with their directories and files.

    Args:
        config: Application configuration
        force: If True, regenerate files even if they exist

    Returns:
        List of initialized space IDs
    """
    initialized = []

    for space in config.spaces.values():
        created = initialize_space(config, space, force)
        if created:
            initialized.append(space.id)

    return initialized


def initialize_space(config: AppConfig, space, force: bool = False) -> bool:
    """Initialize a single space.

    Args:
        config: Application configuration
        space: Space to initialize
        force: If True, regenerate files even if they exist

    Returns:
        True if any files were created/updated
    """
    import json

    created = False
    devices = config.get_devices_for_space(space)

    # Create directory structure
    space.path.mkdir(parents=True, exist_ok=True)
    space.logs_path.mkdir(exist_ok=True)

    # Generate CLAUDE.md
    if force or not space.claude_md_path.exists():
        content = generate_claude_md(space, devices)
        space.claude_md_path.write_text(content)
        created = True
        print(f"  Created: {space.claude_md_path}")

    # Generate .mcp.json
    if force or not space.mcp_json_path.exists():
        mcp_config = generate_mcp_json(devices)
        with open(space.mcp_json_path, "w") as f:
            json.dump(mcp_config, f, indent=2)
        created = True
        print(f"  Created: {space.mcp_json_path}")

    # Create a README in logs folder
    logs_readme = space.logs_path / "README.md"
    if force or not logs_readme.exists():
        logs_readme.write_text(f"""# {space.name} Logs

This folder contains logs and documentation generated during Claude sessions.

## Recommended Structure

- `session-YYYY-MM-DD.md` - Daily session notes
- `changes.md` - Configuration and system changes
- `issues.md` - Problems encountered and resolutions
""")
        created = True

    return created


def copy_example_config(dest: Path = None) -> Path:
    """Copy the example config to the appropriate location.

    Args:
        dest: Destination path. If None, uses ./config/config.yaml

    Returns:
        Path to the created config file
    """
    if dest is None:
        dest = Path.cwd() / "config" / "config.yaml"

    example = Path(__file__).parent.parent.parent / "config" / "config.example.yaml"

    if not example.exists():
        # Try from package
        example = Path.cwd() / "config" / "config.example.yaml"

    if not example.exists():
        raise FileNotFoundError("Could not find config.example.yaml")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(example, dest)

    return dest


def setup_cli():
    """CLI entry point for setup commands."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude LAN Manager Setup Utilities"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize spaces from configuration"
    )
    init_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Regenerate files even if they exist"
    )
    init_parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to config file"
    )

    # copy-config command
    copy_parser = subparsers.add_parser(
        "copy-config",
        help="Copy example config to config/config.yaml"
    )
    copy_parser.add_argument(
        "--dest", "-d",
        type=Path,
        help="Destination path"
    )

    # show-config command
    subparsers.add_parser(
        "show-config",
        help="Show current configuration"
    )

    args = parser.parse_args()

    if args.command == "init":
        config = AppConfig.load(args.config)
        print(f"Spaces base path: {config.spaces_base_path}")
        print(f"Initializing {len(config.spaces)} spaces...")

        initialized = initialize_spaces(config, args.force)

        if initialized:
            print(f"\nInitialized {len(initialized)} spaces:")
            for space_id in initialized:
                print(f"  - {space_id}")
        else:
            print("\nAll spaces already initialized. Use --force to regenerate.")

    elif args.command == "copy-config":
        try:
            dest = copy_example_config(args.dest)
            print(f"Config copied to: {dest}")
            print("Edit this file to configure your devices and spaces.")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return 1

    elif args.command == "show-config":
        config = AppConfig.load()
        print(f"Spaces base path: {config.spaces_base_path}")
        print(f"Terminal: {config.terminal_emulator}")
        print(f"Claude command: {config.claude_code_cmd}")
        print(f"\nDevices ({len(config.devices)}):")
        for dev in config.devices.values():
            print(f"  - {dev.id}: {dev.name} ({dev.ip}:{dev.mcp_port})")
        print(f"\nSpaces ({len(config.spaces)}):")
        for space in config.spaces.values():
            print(f"  - {space.id}: {space.name} [{space.category}] -> {space.devices}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(setup_cli())
