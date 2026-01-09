# Claude LAN Manager

WIP/Planning Notes:

GUI launcher for managing local network computers using Claude Code as the AI agent.

## What It Does

- Launches preconfigured "Claude Spaces" for managing LAN devices
- Each space has isolated MCP configurations (no user-level bleed-through)
- Reduces manual overhead for routine systems administration

## Claude Spaces

Each space is a directory containing:
- `CLAUDE.md` - Role and context for the assistant
- `mcp.json` - Space-specific MCP configuration
- `logs/` - Persistent logging

## Target Devices

| Device | IP | Purpose |
|--------|-----|---------|
| Ubuntu VM | 10.0.0.4 | Home server |
| Raspberry Pi | 10.0.0.63 | Alarm panel |
| Router | 10.0.0.1 | Network gateway |
| Home Assistant | 10.0.0.3 | Home automation |

## Requirements

- Ubuntu 25.x with KDE Plasma
- Python (via `uv`)
- PyQt6

## Status

Planning phase - see [specification.md](./Planning/specification.md) for details.
