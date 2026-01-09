"""Main GUI application for Claude LAN Manager."""

import sys
from pathlib import Path
from functools import partial

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QFrame,
    QMessageBox,
    QScrollArea,
    QGroupBox,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from claude_lan_manager.config import AppConfig, Space
from claude_lan_manager.launcher import (
    launch_claude_in_terminal,
    check_terminal_available,
    check_claude_available,
)


class SpaceButton(QPushButton):
    """Custom button for launching a Claude Space."""

    def __init__(self, space: Space, parent=None):
        super().__init__(parent)
        self.space = space

        # Set button text with device count indicator
        device_count = len(space.devices)
        if device_count == 1:
            count_text = "1 device"
        else:
            count_text = f"{device_count} devices"

        self.setText(f"{space.name}\n({count_text})")

        # Style based on category
        self.setMinimumSize(QSize(150, 80))
        self.setMaximumSize(QSize(200, 100))

        # Set tooltip with description
        if space.description:
            self.setToolTip(space.description)

        # Apply category-specific styling
        self._apply_style()

    def _apply_style(self):
        """Apply styling based on space category."""
        base_style = """
            QPushButton {
                font-size: 12px;
                font-weight: 600;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid;
            }
            QPushButton:pressed {
                padding-top: 14px;
                padding-bottom: 10px;
            }
        """

        if self.space.category == "consolidated":
            # Blue for consolidated/LAN manager
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #4a90d9;
                    border-color: #3a7bc8;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #5a9fe8;
                    border-color: #4a8fd7;
                }
            """)
        elif self.space.category == "group":
            # Teal for group managers
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #26a69a;
                    border-color: #1e8e82;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #2ebfb1;
                    border-color: #26a69a;
                }
            """)
        else:
            # Light gray/blue for individual devices
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #6c8ebf;
                    border-color: #5a7cad;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #7c9ecf;
                    border-color: #6c8ebf;
                }
            """)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config

        self.setWindowTitle("Claude LAN Manager")
        self.setMinimumSize(600, 400)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("Claude LAN Manager")
        header.setFont(QFont("Sans", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # Subtitle showing spaces path
        subtitle = QLabel(f"Spaces: {config.spaces_base_path}")
        subtitle.setStyleSheet("color: #888; font-size: 10px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        # Scroll area for buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        main_layout.addWidget(scroll)

        scroll_content = QWidget()
        scroll.setWidget(scroll_content)
        content_layout = QVBoxLayout(scroll_content)

        # Group spaces by category
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

        # Add consolidated section (LAN Manager)
        if consolidated:
            group_box = QGroupBox("LAN Manager")
            group_layout = QHBoxLayout(group_box)
            group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            for space in consolidated:
                btn = SpaceButton(space)
                btn.clicked.connect(partial(self._launch_space, space))
                group_layout.addWidget(btn)
            content_layout.addWidget(group_box)

        # Add group managers section
        if groups:
            group_box = QGroupBox("Device Groups")
            group_layout = QHBoxLayout(group_box)
            group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            for space in groups:
                btn = SpaceButton(space)
                btn.clicked.connect(partial(self._launch_space, space))
                group_layout.addWidget(btn)
            content_layout.addWidget(group_box)

        # Add individual devices section
        if individual:
            group_box = QGroupBox("Individual Devices")
            grid_layout = QGridLayout(group_box)

            cols = 3
            for i, space in enumerate(individual):
                row = i // cols
                col = i % cols
                btn = SpaceButton(space)
                btn.clicked.connect(partial(self._launch_space, space))
                grid_layout.addWidget(btn, row, col)

            content_layout.addWidget(group_box)

        # Add stretch at bottom
        content_layout.addStretch()

        # Status bar
        self.statusBar().showMessage("Ready")

        # Check prerequisites
        self._check_prerequisites()

    def _check_prerequisites(self):
        """Check that terminal and Claude are available."""
        warnings = []

        if not check_terminal_available(self.config.terminal_emulator):
            warnings.append(f"Terminal '{self.config.terminal_emulator}' not found")

        if not check_claude_available(self.config.claude_code_cmd):
            warnings.append(f"Claude Code '{self.config.claude_code_cmd}' not found")

        if warnings:
            self.statusBar().showMessage(" | ".join(warnings))
            self.statusBar().setStyleSheet("color: orange;")

    def _launch_space(self, space: Space):
        """Launch Claude Code in the specified space."""
        try:
            self.statusBar().showMessage(f"Launching {space.name}...")
            launch_claude_in_terminal(self.config, space)
            self.statusBar().showMessage(f"Launched {space.name}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Launch Error",
                f"Failed to launch {space.name}:\n{str(e)}"
            )
            self.statusBar().showMessage("Launch failed")


def main():
    """Main entry point for the application."""
    # Load configuration
    config = AppConfig.load()

    # If no spaces configured, show a helpful message
    if not config.spaces:
        print("No spaces configured. Please create a config file at:")
        print("  ./config/config.yaml")
        print("  or ~/.config/claude-lan-manager/config.yaml")
        print("\nSee config/config.example.yaml for an example configuration.")
        sys.exit(1)

    # Create Qt application
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
        QGroupBox {
            font-weight: bold;
            font-size: 13px;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-top: 14px;
            padding-top: 12px;
            background-color: #fff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
            color: #555;
        }
        QStatusBar {
            background-color: #e8e8e8;
            color: #666;
            border-top: 1px solid #ddd;
        }
        QScrollArea {
            border: none;
            background-color: #f5f5f5;
        }
    """)

    # Create and show main window
    window = MainWindow(config)
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
