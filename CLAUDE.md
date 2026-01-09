# Claude LAN Manager

## Project Overview

Claude LAN Manager is a GUI launcher application for managing local network computers using Claude Code as the AI agent. It implements "Claude Spaces" - preconfigured environments with dedicated context and MCP configurations for administering specific machines or groups of machines.

## Objective

Create a desktop application that:
1. Displays buttons for preconfigured "assistants" (LAN Manager, individual device managers, group managers)
2. Launches Claude Code in a terminal at the correct subdirectory when clicked
3. Ensures Claude inherits only the MCP configuration defined in that space (no user-level MCP bleed-through)
4. Reduces manual overhead when using Claude for routine systems administration

## Key Concepts

### Claude Spaces
A directory containing:
- `CLAUDE.md` - Role and context for the assistant
- `mcp.json` - MCP configuration (should be the ONLY MCPs available)
- `logs/` - Persistent logging subfolder

### MCP Strategy
- All devices run lightweight MCP servers using **Streamable HTTP** transport
- MCPs are unauthenticated on local network (10.0.0.0/24)
- MCP provides lower overhead than SSH, especially on constrained devices

## Target Environment

- **OS:** Ubuntu 25.x
- **Desktop:** KDE Plasma (Wayland)
- **Terminal:** Konsole
- **Python:** Use `uv` for virtual environments
- **GUI Framework:** PyQt6 (recommended for KDE integration)

## Project Structure

```
claude-lan-manager/
├── Planning/                     # Planning documents and original notes
│   ├── idea-notes.mp3            # Original audio note
│   ├── transcript-cleaned.md     # Cleaned transcript
│   ├── transcript-verbatim.md    # Verbatim transcript
│   └── specification.md          # Development specification
├── app/                          # GUI application (to be created)
├── spaces/                       # Claude Space configurations (to be created)
└── config/                       # App configuration (to be created)
```

## Development Guidelines

1. **Python Environment:** Create `.venv` with `uv` before installing dependencies
2. **GUI:** Use PyQt6 for native KDE Plasma integration
3. **Testing:** Test MCP isolation carefully - this is a critical requirement
4. **Logging:** Ensure logs are written to the `logs/` subfolder within each space

## Key Files

- [Development Specification](./Planning/specification.md) - Full technical specification
- [Original Audio Note](./Planning/idea-notes.mp3) - Voice memo with original idea
- [Cleaned Transcript](./Planning/transcript-cleaned.md) - Readable version of the notes

## Network Devices (Initial Targets)

| Device | IP | Purpose |
|--------|-----|---------|
| Ubuntu VM | 10.0.0.4 | Home server |
| Raspberry Pi | 10.0.0.63 | Alarm panel |
| Router | 10.0.0.1 | Network gateway |
| Home Assistant | 10.0.0.3 | Home automation |

## Current Status

**Phase:** Planning/Specification

The project is currently in the planning phase. The specification document outlines the full implementation approach. Development has not yet begun.
