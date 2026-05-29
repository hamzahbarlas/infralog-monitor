import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── Data Classes ─────────────────────────────────────────────

class LogEvent:
    def __init__(self, timestamp, severity, server, message):
        self.timestamp = timestamp
        self.severity = severity
        self.server = server
        self.message = message

    def __repr__(self):
        return f"[{self.severity}] {self.server}: {self.message}"


class ParsedReport:
    def __init__(self):
        self.total_events = 0
        self.severity_counts = defaultdict(int)
        self.server_counts = defaultdict(int)
        self.brute_force_ips = []
        self.unauthorized_access = []
        self.off_hours_logins = []
        self.resource_critical = []
        self.service_crashes = []
        self.parse_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.source_file = ""

# ── Parser ───────────────────────────────────────────────────

LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\|\s+"
    r"(?P<severity>\w+)\s+\|\s+"
    r"(?P<server>[\w-]+)\s+\|\s+"
    r"(?P<message>.+)"
)

def parse_line(line):
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None
    return LogEvent(
        timestamp=match.group("timestamp"),
        severity=match.group("severity").strip(),
        server=match.group("server").strip(),
        message=match.group("message").strip()
    )

def detect_incidents(event, report):
    msg = event.message.lower()
    severity = event.severity

    # Auth incidents
    if "brute force" in msg or "multiple failed logins" in msg:
        report.brute_force_ips.append({
            "server": event.server,
            "message": event.message,
            "timestamp": event.timestamp
        })

    if "unauthorized access" in msg:
        report.unauthorized_access.append({
            "server": event.server,
            "message": event.message,
            "timestamp": event.timestamp
        })

    if "outside business hours" in msg:
        report.off_hours_logins.append({
            "server": event.server,
            "message": event.message,
            "timestamp": event.timestamp
        })

    # Resource incidents
    if severity == "CRITICAL" and any(x in msg for x in ["cpu", "memory", "disk"]):
        report.resource_critical.append({
            "server": event.server,
            "message": event.message,
            "timestamp": event.timestamp
        })

    # Stability incidents
    if "crashed" in msg or "restart" in msg or "exhausted" in msg:
        report.service_crashes.append({
            "server": event.server,
            "message": event.message,
            "timestamp": event.timestamp
        })

def parse_log_file(filepath):
    path = Path(filepath)
    report = ParsedReport()
    report.source_file = path.name

    with open(path, "r") as f:
        for line in f:
            event = parse_line(line)
            if not event:
                continue

            report.total_events += 1
            report.severity_counts[event.severity] += 1
            report.server_counts[event.server] += 1
            detect_incidents(event, report)

    return report

# ── Quick Test ───────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from rich.console import Console
    from rich.table import Table

    console = Console()

    if len(sys.argv) < 2:
        # Auto find the latest log file
        logs = sorted(Path("logs/incoming").glob("*.log"))
        if not logs:
            print("No log files found. Run the generator first.")
            sys.exit(1)
        filepath = logs[-1]
    else:
        filepath = sys.argv[1]

    console.print(f"\n[bold cyan]Parsing:[/bold cyan] {filepath}\n")
    report = parse_log_file(filepath)

    # Severity summary table
    table = Table(title="Event Summary by Severity")
    table.add_column("Severity", style="bold")
    table.add_column("Count", justify="right")

    colors = {"CRITICAL": "red", "ERROR": "orange3",
              "WARNING": "yellow", "INFO": "green"}
    for severity in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
        count = report.severity_counts.get(severity, 0)
        color = colors.get(severity, "white")
        table.add_row(f"[{color}]{severity}[/{color}]", str(count))

    console.print(table)

    # Top servers
    console.print("\n[bold cyan]Top Troubled Servers:[/bold cyan]")
    sorted_servers = sorted(report.server_counts.items(),
                           key=lambda x: x[1], reverse=True)
    for server, count in sorted_servers[:3]:
        console.print(f"  {server}: {count} events")

    # Incidents
    console.print(f"\n[bold red]Brute Force Attempts:[/bold red] {len(report.brute_force_ips)}")
    console.print(f"[bold red]Unauthorized Access:[/bold red] {len(report.unauthorized_access)}")
    console.print(f"[bold yellow]Off Hours Logins:[/bold yellow] {len(report.off_hours_logins)}")
    console.print(f"[bold red]Critical Resource Events:[/bold red] {len(report.resource_critical)}")
    console.print(f"[bold red]Service Crashes/Restarts:[/bold red] {len(report.service_crashes)}")
    console.print(f"\n[bold green]Total Events Parsed:[/bold green] {report.total_events}\n")