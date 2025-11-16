"""
UNIBOS TUI Action Handlers
Base classes and utilities for handling menu actions
"""

import subprocess
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path

from core.clients.cli.framework.ui import Colors, clear_screen


class ActionHandler(ABC):
    """Base class for action handlers"""

    def __init__(self, tui):
        """
        Initialize handler with TUI reference

        Args:
            tui: Parent TUI instance
        """
        self.tui = tui

    @abstractmethod
    def handle(self, item: Any) -> bool:
        """
        Handle action for menu item

        Args:
            item: Menu item to handle

        Returns:
            True to continue, False to exit
        """
        pass

    def execute_command(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """
        Execute a command and return result

        Args:
            command: Command to execute
            **kwargs: Additional arguments for subprocess.run

        Returns:
            CompletedProcess object
        """
        defaults = {
            'capture_output': True,
            'text': True,
            'check': False
        }
        defaults.update(kwargs)
        return subprocess.run(command, **defaults)

    def show_output(self, result: subprocess.CompletedProcess):
        """
        Show command output

        Args:
            result: CompletedProcess from execute_command
        """
        clear_screen()

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(f"{Colors.RED}{result.stderr}{Colors.RESET}", file=sys.stderr)

        if result.returncode != 0:
            print(f"\n{Colors.RED}Command failed with exit code {result.returncode}{Colors.RESET}")

        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()

    def get_input(self, prompt: str, default: str = "") -> str:
        """
        Get user input

        Args:
            prompt: Input prompt
            default: Default value if empty

        Returns:
            User input string
        """
        clear_screen()
        print(f"{Colors.YELLOW}{prompt}{Colors.RESET}", end="")
        if default:
            print(f" [{default}]", end="")
        print(": ", end="")

        value = input().strip()
        return value if value else default

    def confirm(self, message: str) -> bool:
        """
        Get user confirmation

        Args:
            message: Confirmation message

        Returns:
            True if confirmed, False otherwise
        """
        response = self.get_input(f"{message} (y/n)", "n")
        return response.lower() in ['y', 'yes']


class CommandActionHandler(ActionHandler):
    """Handler that executes CLI commands"""

    def __init__(self, tui, command_template: List[str]):
        """
        Initialize with command template

        Args:
            tui: Parent TUI instance
            command_template: Command template (can include {placeholders})
        """
        super().__init__(tui)
        self.command_template = command_template

    def handle(self, item: Any) -> bool:
        """Execute the command"""
        command = self.build_command(item)
        result = self.execute_command(command)
        self.show_output(result)
        return True

    def build_command(self, item: Any) -> List[str]:
        """
        Build command from template

        Args:
            item: Menu item

        Returns:
            Command list
        """
        command = []
        for part in self.command_template:
            if '{' in part:
                # Simple template substitution
                part = part.format(
                    item_id=item.id,
                    label=item.label
                )
            command.append(part)
        return command


class DjangoActionHandler(ActionHandler):
    """Handler for Django management commands"""

    def __init__(self, tui, management_command: str):
        """
        Initialize with Django management command

        Args:
            tui: Parent TUI instance
            management_command: Django management command name
        """
        super().__init__(tui)
        self.management_command = management_command

    def handle(self, item: Any) -> bool:
        """Execute Django command"""
        # Get Django path
        django_path = self.get_django_path()
        python = self.get_django_python()

        # Build command
        command = [python, 'manage.py', self.management_command]

        # Set environment
        import os
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
        env['PYTHONPATH'] = f"{django_path}:{django_path.parent.parent.parent}"

        # Execute
        result = self.execute_command(command, cwd=str(django_path), env=env)
        self.show_output(result)
        return True

    def get_django_path(self) -> Path:
        """Get path to Django project"""
        # Try git root first
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                check=True
            )
            root_dir = Path(result.stdout.strip())
        except:
            # Fallback to relative path
            root_dir = Path(__file__).parent.parent.parent.parent

        return root_dir / 'core' / 'clients' / 'web'

    def get_django_python(self) -> str:
        """Get Python executable for Django"""
        django_path = self.get_django_path()
        venv_python = django_path / 'venv' / 'bin' / 'python3'

        if venv_python.exists():
            return str(venv_python)

        return 'python3'


class GitActionHandler(ActionHandler):
    """Handler for Git operations"""

    def __init__(self, tui, operation: str):
        """
        Initialize with git operation

        Args:
            tui: Parent TUI instance
            operation: Git operation (status, pull, push, etc)
        """
        super().__init__(tui)
        self.operation = operation

    def handle(self, item: Any) -> bool:
        """Execute git operation"""
        if self.operation == 'status':
            result = self.execute_command(['git', 'status'])
            self.show_output(result)

        elif self.operation == 'pull':
            result = self.execute_command(['git', 'pull'])
            self.show_output(result)

        elif self.operation == 'push':
            message = self.get_input("Enter commit message")
            if message:
                # Add all changes
                self.execute_command(['git', 'add', '-A'])
                # Commit
                self.execute_command(['git', 'commit', '-m', message])
                # Push
                result = self.execute_command(['git', 'push'])
                self.show_output(result)

        return True