#!/usr/bin/env python3
"""
Simple MCP Server for Remote Command Execution

A lightweight MCP (Model Context Protocol) server that allows Claude to execute
shell commands on a remote machine. This is the minimal MCP implementation needed
for Claude LAN Manager.

Transport: Streamable HTTP (not SSE)
Authentication: None (local network use only)

SECURITY WARNING: This server executes arbitrary shell commands with no authentication.
Only run on trusted local networks. Never expose to the internet.

Usage:
    # Install dependencies
    pip install mcp[server]

    # Run the server
    python server.py

    # Or with custom port
    PORT=3001 python server.py
"""

import asyncio
import os
import subprocess
from typing import Any

from mcp.server import Server
from mcp.server.transports.streamable_http import StreamableHTTPTransport
from mcp.types import Tool, TextContent


# Configuration
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "3000"))
HOSTNAME = os.environ.get("DEVICE_HOSTNAME", os.uname().nodename)

# Create the MCP server
server = Server(name=f"{HOSTNAME}-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="run_command",
            description=f"Execute a shell command on {HOSTNAME}",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 60)",
                        "default": 60
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="read_file",
            description=f"Read a file from {HOSTNAME}",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file",
            description=f"Write content to a file on {HOSTNAME}",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="get_system_info",
            description=f"Get system information from {HOSTNAME}",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a tool call."""

    if name == "run_command":
        command = arguments["command"]
        timeout = arguments.get("timeout", 60)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return [TextContent(type="text", text=output or "(no output)")]
        except subprocess.TimeoutExpired:
            return [TextContent(type="text", text=f"Command timed out after {timeout} seconds")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error executing command: {e}")]

    elif name == "read_file":
        path = arguments["path"]
        try:
            with open(path, "r") as f:
                content = f.read()
            return [TextContent(type="text", text=content)]
        except FileNotFoundError:
            return [TextContent(type="text", text=f"File not found: {path}")]
        except PermissionError:
            return [TextContent(type="text", text=f"Permission denied: {path}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading file: {e}")]

    elif name == "write_file":
        path = arguments["path"]
        content = arguments["content"]
        try:
            with open(path, "w") as f:
                f.write(content)
            return [TextContent(type="text", text=f"Successfully wrote to {path}")]
        except PermissionError:
            return [TextContent(type="text", text=f"Permission denied: {path}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error writing file: {e}")]

    elif name == "get_system_info":
        try:
            info_commands = {
                "hostname": "hostname",
                "uptime": "uptime",
                "memory": "free -h | head -2",
                "disk": "df -h / | tail -1",
                "cpu": "cat /proc/cpuinfo | grep 'model name' | head -1",
                "os": "cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2",
            }

            results = []
            for label, cmd in info_commands.items():
                try:
                    output = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=5
                    ).stdout.strip()
                    results.append(f"{label}: {output}")
                except Exception:
                    results.append(f"{label}: (unavailable)")

            return [TextContent(type="text", text="\n".join(results))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting system info: {e}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    print(f"Starting MCP server for {HOSTNAME}")
    print(f"Listening on http://{HOST}:{PORT}/mcp")
    print("Press Ctrl+C to stop")

    transport = StreamableHTTPTransport(
        host=HOST,
        port=PORT,
        path="/mcp"
    )

    await server.run(transport)


if __name__ == "__main__":
    asyncio.run(main())
