# Simple MCP Server for LAN Devices

A minimal MCP (Model Context Protocol) server that enables Claude to execute commands on remote machines. This is the "endpoint" component needed on each device you want to manage with Claude LAN Manager.

## What This Does

When installed on a device, this server exposes a simple HTTP endpoint that Claude can use to:
- Execute shell commands
- Read files
- Write files
- Get system information

## Security Warning

This server executes arbitrary shell commands with **no authentication**. It is designed for use on trusted local networks only.

**Never expose this server to the internet.**

## Installation

### Quick Install (Single File)

```bash
# On the target device
pip install "mcp[server]"

# Download and run
curl -O https://raw.githubusercontent.com/youruser/claude-lan-manager/main/examples/simple-mcp-server/server.py
python server.py
```

### From Requirements

```bash
# Clone or copy this directory to the target device
pip install -r requirements.txt
python server.py
```

### With uv

```bash
uv pip install "mcp[server]"
uv run server.py
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Interface to bind to |
| `PORT` | `3000` | Port to listen on |
| `DEVICE_HOSTNAME` | System hostname | Name used in tool descriptions |

Example:
```bash
PORT=3001 DEVICE_HOSTNAME="my-server" python server.py
```

## Running as a Service

### systemd (Linux)

Create `/etc/systemd/system/mcp-server.service`:

```ini
[Unit]
Description=MCP Server for Claude LAN Manager
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/server
Environment=PORT=3000
ExecStart=/usr/bin/python3 /path/to/server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
```

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
RUN pip install "mcp[server]"
COPY server.py .

ENV HOST=0.0.0.0
ENV PORT=3000

EXPOSE 3000
CMD ["python", "server.py"]
```

Build and run:
```bash
docker build -t mcp-server .
docker run -d -p 3000:3000 --name mcp-server mcp-server
```

## Testing

Test the MCP endpoint with curl:

```bash
# Check if server is responding
curl http://localhost:3000/mcp

# The actual MCP protocol communication happens via HTTP POST
# with JSON-RPC style messages - Claude handles this automatically
```

## Available Tools

| Tool | Description |
|------|-------------|
| `run_command` | Execute shell commands |
| `read_file` | Read file contents |
| `write_file` | Write content to files |
| `get_system_info` | Get hostname, uptime, memory, disk, CPU, OS |

## Extending

To add more tools, modify `server.py`:

1. Add a new `Tool` definition in `list_tools()`
2. Add the handler in `call_tool()`

Example - adding a "list_directory" tool:

```python
# In list_tools()
Tool(
    name="list_directory",
    description=f"List files in a directory on {HOSTNAME}",
    inputSchema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path"}
        },
        "required": ["path"]
    }
)

# In call_tool()
elif name == "list_directory":
    path = arguments["path"]
    try:
        files = os.listdir(path)
        return [TextContent(type="text", text="\n".join(files))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]
```

## Troubleshooting

### Port already in use
```bash
# Find what's using the port
lsof -i :3000
# Use a different port
PORT=3001 python server.py
```

### Permission denied
The server runs commands as the user who started it. For system administration, you may need to:
- Run as root (not recommended)
- Configure sudo without password for specific commands
- Run as a service user with appropriate permissions

### Firewall blocking connections
```bash
# Ubuntu/Debian
sudo ufw allow 3000/tcp

# CentOS/RHEL
sudo firewall-cmd --add-port=3000/tcp --permanent
sudo firewall-cmd --reload
```
