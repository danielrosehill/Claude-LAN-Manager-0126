# Initial Target Devices for Claude LAN Manager

This document defines the initial pool of devices for the minimal implementation.

## Target Devices

| Name | IP | MCP Port | Description |
|------|-----|----------|-------------|
| Ubuntu Router | 10.0.0.1 | 3001 | Network router running Ubuntu (DHCP/DNS) |
| Proxmox | 10.0.0.2 | TBD | Hypervisor for VMs and containers |
| Home Assistant | 10.0.0.3 | 8123 | Home automation platform |
| Ubuntu VM | 10.0.0.4 | 3000 | General purpose home server |
| Display Pi | 10.0.0.63 | 8222 | Raspberry Pi running alarm panel display |

## Claude Spaces to Create

### 1. LAN Manager (All Devices)
- **Purpose:** Unified management of all target devices
- **MCP Config:** Includes all 5 device endpoints
- **Use cases:** Cross-device operations, network-wide status checks

### 2. Individual Device Managers
Each device gets its own space for focused administration:

- **router-manager** - Ubuntu Router administration
- **proxmox-manager** - VM/container management
- **homeassistant-manager** - Home automation control
- **ubuntuvm-manager** - Server administration
- **displaypi-manager** - Alarm panel / display management

## MCP Endpoint Format

All devices use Streamable HTTP transport. Endpoints follow the pattern:

```
http://{IP}:{PORT}/mcp
```

Example configurations will be provided in `.env.example`.

## Implementation Priority

1. **Phase 1:** Get GUI launcher working with placeholder buttons
2. **Phase 2:** Create space directories with CLAUDE.md and mcp.json
3. **Phase 3:** Verify MCP connectivity to each device
4. **Phase 4:** Test MCP isolation (no user-level MCP bleed-through)
