import subprocess
import time
import os
import sys
import signal
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

console = Console()

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(PROJECT_ROOT, "venv/bin/python")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable # Fallback

processes = []

def start_process(command, name, cwd=PROJECT_ROOT, shell=False):
    """Start a background process"""
    try:
        console.print(f"[bold blue][*] Starting {name}...[/bold blue]")
        # If command is a list and shell is False, use it directly.
        # If shell is True, join it into a string.
        if shell and isinstance(command, list):
            command = " ".join(command)
            
        p = subprocess.Popen(
            command,
            cwd=cwd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid # Create new process group
        )
        processes.append((name, p))
        console.print(f"[bold green][+] {name} started (PID: {p.pid})[/bold green]")
        return p
    except Exception as e:
        console.print(f"[bold red][!] Failed to start {name}: {e}[/bold red]")
        return None

def stop_all():
    """Stop all running processes"""
    console.print("\n[bold yellow][*] Stopping all services...[/bold yellow]")
    for name, p in processes:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            console.print(f"    - Stopped {name}")
        except Exception:
            pass
    sys.exit(0)

def main():
    # Banner
    console.print(Panel.fit(
        "[bold cyan]AURA - Adaptive Unified Response Agent[/bold cyan]\n"
        "[white]System Startup Script[/white]",
        border_style="blue"
    ))

    # Check for Root (Required for IDS/Honeypot)
    if os.geteuid() != 0:
        console.print("[bold red][!] AURA requires root privileges for IDS sniffing and Honeypot binding.[/bold red]")
        console.print("[yellow]    Please run with: sudo python3 start.py[/yellow]")
        sys.exit(1)

    # 1. Start Dashboard API (Flask)
    start_process(
        [VENV_PYTHON, "dashboard/api/app.py"],
        "Dashboard API",
        cwd=PROJECT_ROOT
    )

    # 2. Start Dashboard Frontend (Vite)
    # Note: npm run dev usually requires interactive shell, running in background
    start_process(
        "npm run dev",
        "Dashboard Frontend",
        cwd=os.path.join(PROJECT_ROOT, "dashboard/frontend"),
        shell=True
    )

    # 3. Start IDS Detector
    # Note: Needs to run in background, logging to console/file
    start_process(
        [VENV_PYTHON, "IDS/main.py"],
        "IDS Detector",
        cwd=PROJECT_ROOT
    )

    # 4. Start Honeypot Controller
    start_process(
        [VENV_PYTHON, "HONEYPOT/controller.py"],
        "Honeypot Controller",
        cwd=PROJECT_ROOT
    )
    
    # 5. Start OSINT Harvester (Periodic)
    # We run it once on startup, then it might schedule itself or we leave it running if it has a loop
    start_process(
        [VENV_PYTHON, "osint-harvester/main.py"],
        "OSINT Harvester",
        cwd=PROJECT_ROOT
    )

    console.print("\n[bold green]All systems initialized![/bold green]")
    console.print("[white]Dashboard available at: http://localhost:5173[/white]")
    console.print("[white]API available at: http://localhost:5000[/white]")
    console.print("[yellow]Press Ctrl+C to shutdown.[/yellow]")

    # Monitor Loop
    try:
        while True:
            time.sleep(5)
            # Check if processes are still alive
            for name, p in processes:
                if p.poll() is not None:
                    console.print(f"[bold red][!] {name} died unexpectedly! (Exit Code: {p.returncode})[/bold red]")
                    # Optional: Restart logic
    except KeyboardInterrupt:
        stop_all()

if __name__ == "__main__":
    main()
