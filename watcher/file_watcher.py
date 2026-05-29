import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console

# Add project root to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from parser.log_parser import parse_log_file
from reporter.report_builder import save_report

console = Console()

# ── Config ───────────────────────────────────────────────────

WATCH_DIR = Path("logs/incoming")
WATCH_DIR.mkdir(parents=True, exist_ok=True)

# ── Event Handler ────────────────────────────────────────────

class LogFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Ignore directory events
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Only process .log files
        if filepath.suffix != ".log":
            return

        console.print(f"\n[bold cyan][WATCHER][/bold cyan] New file detected: {filepath.name}")

        # Small delay to make sure file is fully written
        time.sleep(1)

        try:
            # Step 1 - Parse
            console.print(f"[bold yellow]  >> Parsing...[/bold yellow]")
            report = parse_log_file(filepath)

            # Step 2 - Report
            console.print(f"[bold yellow]  >> Building report...[/bold yellow]")
            filename, content = save_report(report)

            # Step 3 - Summary
            critical = report.severity_counts.get("CRITICAL", 0)
            error = report.severity_counts.get("ERROR", 0)
            risk_score = min(100, (critical * 3) + (error * 1))

            if risk_score >= 70:
                risk_color = "red"
            elif risk_score >= 40:
                risk_color = "yellow"
            else:
                risk_color = "green"

            console.print(f"[bold green]  >> Report saved:[/bold green] {filename}")
            console.print(f"  >> Events: {report.total_events} | "
                         f"Critical: {critical} | "
                         f"Risk: [{risk_color}]{risk_score}/100[/{risk_color}]")

            # Step 4 - Alert if high risk
            if risk_score >= 70:
                console.print(f"\n[bold red]  !! HIGH RISK ALERT - "
                             f"Score {risk_score}/100 !![/bold red]")
                console.print(f"[bold red]  !! Email notification would fire here[/bold red]")

        except Exception as e:
            console.print(f"[bold red]  >> Error processing {filepath.name}: {e}[/bold red]")


# ── Main Watcher ─────────────────────────────────────────────

def start_watcher():
    console.print(f"\n[bold cyan]InfraLog Monitor - File Watcher[/bold cyan]")
    console.print(f"[bold cyan]Watching:[/bold cyan] {WATCH_DIR.resolve()}")
    console.print(f"Press [bold]Ctrl+C[/bold] to stop\n")

    event_handler = LogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Watcher stopped[/bold yellow]")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    start_watcher()