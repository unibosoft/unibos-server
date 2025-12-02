"""
UNIBOS CLI - Development Commands
Local development server (uvicorn), shell, tests, migrations
"""

import click
import subprocess
import sys
import os
import signal
from pathlib import Path


# PID file for tracking server process
PID_FILE = Path.home() / '.cache' / 'unibos' / 'dev_server.pid'


def get_django_path():
    """Get path to Django manage.py"""
    # Use git to find repository root (works from anywhere in the repo)
    import subprocess as sp
    result = sp.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode == 0:
        root_dir = Path(result.stdout.strip())
    else:
        # Fallback to __file__ based path
        root_dir = Path(__file__).parent.parent.parent.parent

    return root_dir / 'core' / 'clients' / 'web'


def get_project_root():
    """Get UNIBOS project root directory"""
    django_path = get_django_path()
    return django_path.parent.parent.parent


def get_django_python():
    """Get Python executable from Django venv, fallback to system Python"""
    django_path = get_django_path()
    venv_python = django_path / 'venv' / 'bin' / 'python3'

    if venv_python.exists():
        return str(venv_python)

    # Fallback to system python3
    return 'python3'


def get_uvicorn_cmd():
    """Get uvicorn command - uses python -m uvicorn for reliability"""
    python_bin = get_django_python()
    return [python_bin, '-m', 'uvicorn']


def save_pid(pid: int):
    """Save server PID to file"""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(pid))


def get_pid() -> int:
    """Get saved server PID"""
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except:
            pass
    return None


def clear_pid():
    """Clear PID file"""
    if PID_FILE.exists():
        PID_FILE.unlink()


def is_server_running() -> tuple:
    """Check if server is running, returns (running, pid)"""
    # First check PID file
    pid = get_pid()
    if pid:
        try:
            os.kill(pid, 0)  # Check if process exists
            return True, pid
        except OSError:
            clear_pid()

    # Fallback: check for running uvicorn process via pgrep
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'uvicorn.*unibos_backend'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            # Found running process, get first PID
            found_pid = int(result.stdout.strip().split('\n')[0])
            return True, found_pid
    except:
        pass

    return False, None


@click.group(name='dev')
def dev_group():
    """💻 Development commands"""
    pass


@dev_group.command(name='run')
@click.option('--port', default=8000, help='Port to run on')
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--reload/--no-reload', default=True, help='Enable auto-reload')
@click.option('--background', '-b', is_flag=True, help='Run in background')
def dev_run(port, host, reload, background):
    """Run ASGI development server (uvicorn)"""
    # Check if already running
    running, pid = is_server_running()
    if running:
        click.echo(click.style(f'⚠️  server already running (pid: {pid})', fg='yellow'))
        click.echo(click.style(f'   stop with: unibos-dev dev stop', fg='yellow'))
        return

    django_path = get_django_path()
    root_dir = get_project_root()

    if not (django_path / 'manage.py').exists():
        click.echo(click.style(f'❌ error: manage.py not found in {django_path}', fg='red'))
        sys.exit(1)

    # Set environment
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{root_dir}"

    # Build uvicorn command using python -m uvicorn
    uvicorn_cmd = get_uvicorn_cmd()
    cmd = uvicorn_cmd + [
        'unibos_backend.asgi:application',
        '--host', host,
        '--port', str(port),
        '--log-level', 'info',
    ]

    if reload:
        cmd.extend(['--reload', '--reload-dir', str(django_path)])

    if background:
        click.echo(click.style(f'🚀 starting uvicorn server on {host}:{port} (background)...', fg='cyan', bold=True))

        # Start in background
        process = subprocess.Popen(
            cmd,
            cwd=str(django_path),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        save_pid(process.pid)
        click.echo(click.style(f'✅ server started (pid: {process.pid})', fg='green'))
        click.echo(click.style(f'   url: http://{host}:{port}', fg='cyan'))
        click.echo(click.style(f'   stop with: unibos-dev dev stop', dim=True))
    else:
        click.echo(click.style(f'🚀 starting uvicorn server on {host}:{port}...', fg='cyan', bold=True))
        click.echo(click.style(f'   asgi application: unibos_backend.asgi:application', dim=True))
        click.echo(click.style(f'   auto-reload: {"enabled" if reload else "disabled"}', dim=True))
        click.echo()

        try:
            process = subprocess.Popen(cmd, cwd=str(django_path), env=env)
            save_pid(process.pid)
            process.wait()
        except KeyboardInterrupt:
            click.echo(click.style('\n👋 server stopped', fg='yellow'))
        finally:
            clear_pid()


@dev_group.command(name='stop')
def dev_stop():
    """Stop development server"""
    import time

    click.echo(click.style('⏹️  stopping development server...', fg='yellow'))

    stopped = False
    running, pid = is_server_running()

    if running and pid:
        try:
            # Kill the process and its children
            os.kill(pid, signal.SIGTERM)
            clear_pid()
            click.echo(click.style(f'✅ server stopped (pid: {pid})', fg='green'))
            stopped = True

            # Wait briefly for process to terminate
            time.sleep(0.3)

            # Verify it's stopped
            try:
                os.kill(pid, 0)
                # Still running, try SIGKILL
                click.echo(click.style(f'   sending SIGKILL...', dim=True))
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass  # Process is gone, good

        except OSError as e:
            click.echo(click.style(f'⚠️  could not stop pid {pid}: {e}', fg='yellow'))
            clear_pid()

    # Fallback: try to find and kill uvicorn processes
    if not stopped:
        try:
            result = subprocess.run(
                ['pkill', '-f', 'uvicorn.*unibos_backend'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                clear_pid()
                click.echo(click.style('✅ server stopped', fg='green'))
                stopped = True
        except:
            pass

    # Also try legacy runserver
    if not stopped:
        try:
            result = subprocess.run(
                ['pkill', '-f', 'manage.py runserver'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                clear_pid()
                click.echo(click.style('✅ server stopped (legacy)', fg='green'))
                stopped = True
        except:
            pass

    # Final check: kill any process using port 8000
    try:
        result = subprocess.run(
            ['lsof', '-ti', ':8000'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for port_pid in pids:
                try:
                    os.kill(int(port_pid), signal.SIGKILL)
                    click.echo(click.style(f'   killed port holder: {port_pid}', dim=True))
                    stopped = True
                except:
                    pass
    except:
        pass

    if not stopped:
        click.echo(click.style('⚠️  no running server found', fg='yellow'))


@dev_group.command(name='status')
def dev_status():
    """Check development server status"""
    running, pid = is_server_running()

    if running:
        click.echo(click.style('✅ server is running', fg='green'))
        click.echo(click.style(f'   pid: {pid}', dim=True))

        # Try to get more info about the process
        try:
            result = subprocess.run(
                ['ps', '-p', str(pid), '-o', 'command='],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                cmd = result.stdout.strip()[:80]
                click.echo(click.style(f'   cmd: {cmd}', dim=True))
        except:
            pass

        # Try to check if port is responding
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            if result == 0:
                click.echo(click.style('   url: http://127.0.0.1:8000', fg='cyan'))
            else:
                click.echo(click.style('   ⚠️  port 8000 not responding', fg='yellow'))
        except:
            pass
    else:
        click.echo(click.style('⚫ server is not running', dim=True))
        click.echo(click.style('   start with: unibos-dev dev run', dim=True))


@dev_group.command(name='shell')
def dev_shell():
    """Open Django shell"""
    click.echo(click.style('🐚 Opening Django shell...', fg='cyan'))

    django_path = get_django_path()
    root_dir = django_path.parent.parent.parent

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{root_dir}"

    try:
        subprocess.run(
            [get_django_python(), 'manage.py', 'shell'],
            cwd=str(django_path),
            env=env
        )
    except KeyboardInterrupt:
        click.echo()


@dev_group.command(name='test')
@click.argument('args', nargs=-1)
def dev_test(args):
    """Run tests"""
    click.echo(click.style('🧪 Running tests...', fg='cyan'))

    django_path = get_django_path()
    root_dir = django_path.parent.parent.parent

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{root_dir}"

    cmd = [get_django_python(), 'manage.py', 'test'] + list(args)

    result = subprocess.run(cmd, cwd=str(django_path), env=env)
    sys.exit(result.returncode)


@dev_group.command(name='migrate')
@click.option('--app', help='Specific app to migrate')
def dev_migrate(app):
    """Run database migrations"""
    click.echo(click.style('🔄 Running migrations...', fg='cyan'))

    django_path = get_django_path()
    root_dir = django_path.parent.parent.parent

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{root_dir}"

    cmd = [get_django_python(), 'manage.py', 'migrate']
    if app:
        cmd.append(app)

    result = subprocess.run(cmd, cwd=str(django_path), env=env)
    sys.exit(result.returncode)


@dev_group.command(name='makemigrations')
@click.option('--app', help='Specific app to create migrations for')
def dev_makemigrations(app):
    """Create new migrations"""
    click.echo(click.style('📝 Creating migrations...', fg='cyan'))

    django_path = get_django_path()
    root_dir = django_path.parent.parent.parent

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{root_dir}"

    cmd = [get_django_python(), 'manage.py', 'makemigrations']
    if app:
        cmd.append(app)

    result = subprocess.run(cmd, cwd=str(django_path), env=env)
    sys.exit(result.returncode)


@dev_group.command(name='logs')
@click.option('--lines', '-n', default=50, help='Number of lines to show')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
def dev_logs(lines, follow):
    """View development logs"""
    click.echo(click.style(f'📋 Showing last {lines} log lines...', fg='cyan'))

    root_dir = Path(__file__).parent.parent.parent.parent
    log_file = root_dir / 'data' / 'core' / 'logs' / 'django' / 'debug.log'

    if not log_file.exists():
        click.echo(click.style(f'⚠️  Log file not found: {log_file}', fg='yellow'))
        return

    try:
        if follow:
            subprocess.run(['tail', '-f', '-n', str(lines), str(log_file)])
        else:
            subprocess.run(['tail', '-n', str(lines), str(log_file)])
    except KeyboardInterrupt:
        click.echo()
