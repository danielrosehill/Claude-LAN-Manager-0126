# Claude LAN Manager - Development Specification

**Version:** 0.1.0 (Planning)
**Date:** 9 Jan 2026
**Source:** [Original audio notes](./idea-notes.mp3) | [Cleaned transcript](./transcript-cleaned.md) | [Verbatim transcript](./transcript-verbatim.md)

---

## Executive Summary

Claude LAN Manager is a GUI application that provides a launcher interface for managing local network computers using Claude Code as the underlying agent. The application creates "Claude Spaces" - preconfigured environments with dedicated `CLAUDE.md` context files and `mcp.json` configurations that allow Claude to administer specific machines or groups of machines via MCP (Model Context Protocol) servers.

## Problem Statement

Currently, using Claude Code for systems administration across multiple local network devices requires manual setup for each session:
- Navigating to the correct directory
- Ensuring the right MCP connections are available
- Providing context about which machine is being managed
- Remembering SSH aliases or connection details

This creates friction and time overhead, especially for routine administration tasks.

## Proposed Solution

A GUI launcher that:
1. Presents preconfigured "assistants" as clickable buttons
2. Opens Claude Code in a terminal at a preconfigured subfolder
3. Automatically loads the correct `CLAUDE.md` and `mcp.json` for that context
4. Provides isolated tool exposure (only the defined MCPs, not user-level MCPs)

## Architecture

### Core Concepts

#### Claude Spaces
A "Claude Space" is a directory containing:
- `CLAUDE.md` - Context file defining the assistant's role and instructions
- `mcp.json` - MCP configuration for that specific context
- `logs/` - Subfolder for persistent logging and documentation

#### MCP Strategy
All network endpoints run lightweight MCP servers using **Streamable HTTP** transport (not SSE). This provides:
- Lower overhead than SSH-based approaches
- Better performance on resource-constrained devices (e.g., Raspberry Pi)
- No authentication required for local network (unauthenticated endpoints)

### Assistant Configurations

#### 1. LAN Manager (Consolidated)
- **Purpose:** Single master assistant for entire home network
- **MCP Config:** Aggregated MCP containing all network endpoints (via MetaMCP or similar)
- **Trade-offs:**
  - Pros: Single point of configuration, easiest to use
  - Cons: Heaviest tool load, potential for confusion between machines

#### 2. Individual Computer Managers
One assistant per computer with dedicated MCP:
- Ubuntu VM / Home Server Manager
- Raspberry Pi Manager
- Router Manager
- Home Assistant Manager
- Other device-specific managers

#### 3. Group Managers (Optional)
Intermediate configurations for related device groups:
- **SBC Manager:** Raspberry Pi + Orange Pi devices (3 MCPs)
- Purpose: Middle ground between single-device and full-network scope

### GUI Requirements

#### Main Window
- Grid or list of assistant buttons
- Visual distinction between:
  - Consolidated LAN Manager
  - Group managers
  - Individual device managers
- Each button labeled with device/group name

#### Launch Behavior
When an assistant button is clicked:
1. Open system terminal (KDE Plasma: Konsole)
2. Navigate to the assistant's Claude Space directory
3. Launch Claude Code
4. Claude inherits `CLAUDE.md` and `mcp.json` from that directory

#### MCP Isolation
Critical requirement: The `mcp.json` in each Claude Space should be the **complete** MCP configuration. User-level MCPs should NOT be inherited or added.

## Directory Structure

```
claude-lan-manager/
├── app/                          # GUI application code
├── spaces/                       # Claude Space configurations
│   ├── lan-manager/              # Consolidated manager
│   │   ├── CLAUDE.md
│   │   ├── mcp.json
│   │   └── logs/
│   ├── ubuntu-vm/                # Individual: Home server
│   │   ├── CLAUDE.md
│   │   ├── mcp.json
│   │   └── logs/
│   ├── raspberry-pi/             # Individual: Raspberry Pi
│   │   ├── CLAUDE.md
│   │   ├── mcp.json
│   │   └── logs/
│   ├── sbc-group/                # Group: All SBCs
│   │   ├── CLAUDE.md
│   │   ├── mcp.json
│   │   └── logs/
│   └── [other-devices]/
└── config/                       # App configuration
    └── devices.json              # Device definitions (IP, name, MCP endpoint)
```

## Technical Considerations

### Target Environment
- **OS:** Linux (Ubuntu 25.x)
- **Desktop:** KDE Plasma (Wayland)
- **Terminal:** Konsole (KDE default)
- **Network:** 10.0.0.0/24 subnet with static IPs

### MCP Server Requirements
Each managed device needs:
- Lightweight MCP server running
- Streamable HTTP transport
- Accessible on local network (unauthenticated)
- Basic system administration tools exposed

### GUI Framework Options
- PyQt6 (native KDE/Qt integration)
- Electron (cross-platform, heavier)
- Tauri (Rust-based, lighter than Electron)
- GTK4 (GNOME-native but works on KDE)

**Recommendation:** PyQt6 for best KDE Plasma integration

## Implementation Phases

### Phase 1: Core Infrastructure
- Define Claude Space directory structure
- Create template `CLAUDE.md` files for each assistant type
- Configure MCP servers on target devices
- Create device configuration schema

### Phase 2: CLI Launcher
- Script-based launcher (proof of concept)
- Validate Claude Space isolation works correctly
- Test MCP connectivity and performance

### Phase 3: GUI Application
- Basic window with assistant buttons
- Terminal launch integration
- Configuration management UI

### Phase 4: Enhancements
- Device status indicators (online/offline)
- Log viewer integration
- Assistant template management
- Add/remove devices dynamically

## Known Network Devices

Initial target devices for implementation:

| Device | IP | Purpose | MCP Endpoint |
|--------|-----|---------|--------------|
| Ubuntu VM | 10.0.0.4 | Home server | TBD |
| Raspberry Pi | 10.0.0.63 | Alarm panel | TBD |
| Router | 10.0.0.1 | Network gateway | TBD |
| Home Assistant | 10.0.0.3 | Home automation | TBD |
| Orange Pi (x2) | TBD | Audio devices | TBD |

## Success Criteria

1. Claude Code launches with correct context in < 3 seconds
2. MCP isolation prevents user-level MCP bleed-through
3. GUI is stable on KDE Plasma/Wayland
4. Reduced time-to-task for routine administration
5. Consistent logging and documentation across sessions

## Open Questions

1. How to handle MCP server deployment/updates across devices?
2. Should the app include health monitoring for MCP endpoints?
3. What's the best way to ensure MCP isolation in Claude Code?
4. Should assistant configurations be version-controlled separately?

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [MetaMCP Aggregator](https://github.com/anthropics/metamcp)
- Claude Code documentation
