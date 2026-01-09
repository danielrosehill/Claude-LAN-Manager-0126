"""Terminal multiplexer GUI for Claude LAN Manager.

Orchestrates Konsole tabs - each target opens a new tab running Claude Code
in the appropriate space with isolated MCP configuration.
"""

import subprocess
import sys
from functools import partial

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QFont

from claude_lan_manager.config import AppConfig, Space


class TargetButton(QPushButton):
    """Button for a target in the sidebar."""

    def __init__(self, space: Space, parent=None):
        super().__init__(parent)
        self.space = space

        device_count = len(space.devices)
        self.setText(f"{space.name}\n{device_count} device{'s' if device_count != 1 else ''}")

        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        if space.description:
            self.setToolTip(space.description)

        self._apply_style()

    def _apply_style(self):
        """Apply styling based on category."""
        if self.space.category == "consolidated":
            color = "#4a90d9"
            hover = "#5a9fe8"
        elif self.space.category == "group":
            color = "#26a69a"
            hover = "#2ebfb1"
        else:
            color = "#6c8ebf"
            hover = "#7c9ecf"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 14px;
                text-align: left;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {color};
            }}
        """)


class MultiplexerWindow(QMainWindow):
    """Main window that orchestrates Konsole tabs."""

    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self.active_sessions: dict[str, int] = {}  # space_id -> PID

        self.setWindowTitle("Claude LAN Manager")
        self.setMinimumSize(280, 500)
        self.setMaximumWidth(320)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QLabel("Claude LAN Manager")
        header.setFont(QFont("Sans", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #333; padding-bottom: 4px;")
        layout.addWidget(header)

        subtitle = QLabel("Click to open Claude in Konsole")
        subtitle.setStyleSheet("color: #666; font-size: 11px; padding-bottom: 8px;")
        layout.addWidget(subtitle)

        # Scroll area for targets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        layout.addWidget(scroll)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll.setWidget(scroll_content)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(6)

        # Group by category
        consolidated = []
        groups = []
        individual = []

        for space in config.spaces.values():
            if space.category == "consolidated":
                consolidated.append(space)
            elif space.category == "group":
                groups.append(space)
            else:
                individual.append(space)

        # Add sections
        if consolidated:
            self._add_section(scroll_layout, "LAN Manager", consolidated)
        if groups:
            self._add_section(scroll_layout, "Groups", groups)
        if individual:
            self._add_section(scroll_layout, "Devices", individual)

        scroll_layout.addStretch()

        # Status bar
        self.statusBar().showMessage("Ready")

    def _add_section(self, layout: QVBoxLayout, title: str, spaces: list[Space]):
        """Add a section of targets."""
        header = QLabel(title)
        header.setStyleSheet("""
            color: #555;
            font-size: 11px;
            font-weight: bold;
            padding: 12px 0 6px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        layout.addWidget(header)

        for space in spaces:
            btn = TargetButton(space)
            btn.clicked.connect(partial(self._launch_space, space))
            layout.addWidget(btn)

    def _launch_space(self, space: Space):
        """Launch Claude in a new Konsole tab for this space."""
        # Build the claude command
        mcp_config = space.mcp_json_path

        claude_cmd = (
            f'cd "{space.path}" && '
            f'{self.config.claude_code_cmd} '
            f'--strict-mcp-config '
            f'--mcp-config "{mcp_config}"'
        )

        # Launch in Konsole with a named tab
        try:
            subprocess.Popen([
                "konsole",
                "--new-tab",
                "-p", f"tabtitle={space.name}",
                "-e", "bash", "-c", claude_cmd
            ])
            self.statusBar().showMessage(f"Opened: {space.name}")
        except FileNotFoundError:
            # Fallback: try generic x-terminal-emulator
            try:
                subprocess.Popen([
                    "x-terminal-emulator",
                    "-e", "bash", "-c", claude_cmd
                ])
                self.statusBar().showMessage(f"Opened: {space.name}")
            except FileNotFoundError:
                self.statusBar().showMessage("Error: No terminal emulator found")


def main():
    """Main entry point."""
    config = AppConfig.load()

    if not config.spaces:
        print("No spaces configured. Please create a config file.")
        print("See config/config.example.yaml for an example.")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("Claude LAN Manager")
    app.setApplicationVersion("0.1.0")

    # Light theme
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QWidget {
            background-color: #f5f5f5;
            color: #333;
        }
        QStatusBar {
            background-color: #e8e8e8;
            color: #666;
            border-top: 1px solid #ddd;
            font-size: 11px;
        }
        QScrollArea {
            background-color: transparent;
        }
    """)

    window = MultiplexerWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
