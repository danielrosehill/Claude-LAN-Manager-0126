# Claude LAN Manager - Development Roadmap

## V1.0 - Current Release

**Status:** Complete

### Features
- **GUI Launcher** (`claude-lan-manager`) - Button-based launcher with light theme
- **Multiplexer** (`claude-lan-mux`) - Sidebar launcher that spawns Konsole tabs
- **Space Management** - Auto-generates CLAUDE.md and .mcp.json for each space
- **MCP Isolation** - Uses `--strict-mcp-config` to prevent user-level MCP bleed-through
- **Example MCP Server** - Lightweight server template for LAN devices

### Commands
```bash
uv run claude-lan-manager        # Button grid launcher
uv run claude-lan-mux            # Sidebar launcher (spawns Konsole tabs)
uv run claude-lan-manager-setup  # Setup utilities
```

---

## V2.0 - Embedded Terminal Multiplexer

**Status:** Planned

### Goal
Create a true multiplexer window with embedded terminals - sidebar on the left, tiled terminal panes on the right, all within a single window.

### Approach Options

1. **QTermWidget Integration**
   - Use `libqtermwidget6` (already available on system)
   - Requires Python bindings (ctypes or custom sip bindings)
   - Most native solution for Qt6

2. **Window Reparenting**
   - Spawn Konsole/xterm instances
   - Capture their window IDs and reparent into Qt container
   - Works on X11, limited on Wayland

3. **VTE via GObject**
   - Use GTK's VTE terminal widget via PyGObject
   - Mix GTK widget into Qt app (possible but messy)

4. **Electron/Tauri Approach**
   - Use xterm.js for web-based terminal emulation
   - Wrap in Electron or Tauri
   - Cross-platform but heavier

### Recommended Path
Start with **QTermWidget** - create Python bindings for the existing system library. This gives native Qt6 integration with proper terminal emulation.

### UI Concept
```
┌──────────────┬─────────────────────────────────────────────┐
│              │  ┌─────────────────┐ ┌─────────────────┐   │
│  Targets     │  │ Router          │ │ Home Server     │   │
│  ─────────   │  │ claude>         │ │ claude>         │   │
│  ● Router    │  │                 │ │                 │   │
│  ● Server    │  └─────────────────┘ └─────────────────┘   │
│  ○ Pi        │  ┌─────────────────┐                       │
│  ○ HA        │  │ Raspberry Pi    │                       │
│              │  │ claude>         │                       │
│              │  │                 │                       │
│              │  └─────────────────┘                       │
└──────────────┴─────────────────────────────────────────────┘
```

- Sidebar shows all targets with active/inactive indicators
- Click to open terminal pane (or focus existing)
- Auto-tiling: 1→full, 2→side-by-side, 3-4→2x2 grid, etc.
- Close button on each pane header

---

## V3.0 - Network Discovery & Health

**Status:** Future

### Features
- **MCP Discovery** - Scan local network for MCP servers
- **Health Monitoring** - Show online/offline status for each device
- **Auto-configuration** - Detect devices and suggest space configurations

### Discovery Approaches
- Port scanning common MCP ports (3000, 8000, etc.)
- mDNS/Avahi service announcements (requires MCP server changes)
- ARP scan + probe known ports

---

## V4.0 - Advanced Features

**Status:** Future

- Session persistence (resume Claude conversations)
- Log aggregation and search
- Device grouping UI
- Configuration sync across machines
- Remote MCP server deployment tools
