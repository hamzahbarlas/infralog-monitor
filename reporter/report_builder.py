from pathlib import Path
from datetime import datetime

# ── Config ───────────────────────────────────────────────────

REPORT_OUTPUT_DIR = Path("logs/reports")
REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Report Builder ───────────────────────────────────────────

def build_report(parsed_report):
    lines = []
    r = parsed_report

    # Header
    lines.append("=" * 60)
    lines.append("       INFRALOG MONITOR - INCIDENT REPORT")
    lines.append("=" * 60)
    lines.append(f"  Generated : {r.parse_time}")
    lines.append(f"  Source    : {r.source_file}")
    lines.append(f"  Total     : {r.total_events} events parsed")
    lines.append("=" * 60)

    # Severity Summary
    lines.append("\n[EVENT SUMMARY BY SEVERITY]")
    lines.append("-" * 40)
    for severity in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
        count = r.severity_counts.get(severity, 0)
        bar = "|" * count
        lines.append(f"  {severity:<10} {count:>4}  {bar}")

    # Top Servers
    lines.append("\n[TOP TROUBLED SERVERS]")
    lines.append("-" * 40)
    sorted_servers = sorted(r.server_counts.items(),
                            key=lambda x: x[1], reverse=True)
    for i, (server, count) in enumerate(sorted_servers[:5], 1):
        lines.append(f"  {i}. {server:<20} {count} events")

    # Auth Incidents
    lines.append("\n[AUTH & ACCESS INCIDENTS]")
    lines.append("-" * 40)

    if r.brute_force_ips:
        lines.append(f"  !! Brute Force Attempts Detected: {len(r.brute_force_ips)}")
        for incident in r.brute_force_ips[:5]:
            lines.append(f"     [{incident['timestamp']}] {incident['server']}")
            lines.append(f"     {incident['message']}")
    else:
        lines.append("  No brute force attempts detected")

    if r.unauthorized_access:
        lines.append(f"\n  !! Unauthorized Access Attempts: {len(r.unauthorized_access)}")
        for incident in r.unauthorized_access[:5]:
            lines.append(f"     [{incident['timestamp']}] {incident['server']}")
            lines.append(f"     {incident['message']}")
    else:
        lines.append("  No unauthorized access attempts detected")

    if r.off_hours_logins:
        lines.append(f"\n  !! Off Hours Login Attempts: {len(r.off_hours_logins)}")
        for incident in r.off_hours_logins[:5]:
            lines.append(f"     [{incident['timestamp']}] {incident['server']}")
            lines.append(f"     {incident['message']}")
    else:
        lines.append("  No off hours logins detected")

    # Resource Incidents
    lines.append("\n[RESOURCE HEALTH INCIDENTS]")
    lines.append("-" * 40)

    if r.resource_critical:
        lines.append(f"  !! Critical Resource Events: {len(r.resource_critical)}")
        for incident in r.resource_critical[:5]:
            lines.append(f"     [{incident['timestamp']}] {incident['server']}")
            lines.append(f"     {incident['message']}")
    else:
        lines.append("  All resources within normal thresholds")

    # Stability Incidents
    lines.append("\n[SERVICE STABILITY INCIDENTS]")
    lines.append("-" * 40)

    if r.service_crashes:
        lines.append(f"  !! Service Crashes/Restarts: {len(r.service_crashes)}")
        for incident in r.service_crashes[:5]:
            lines.append(f"     [{incident['timestamp']}] {incident['server']}")
            lines.append(f"     {incident['message']}")
    else:
        lines.append("  All services stable")

    # Risk Score
    critical = r.severity_counts.get("CRITICAL", 0)
    error = r.severity_counts.get("ERROR", 0)
    risk_score = min(100, (critical * 3) + (error * 1))

    lines.append("\n[RISK SCORE]")
    lines.append("-" * 40)
    if risk_score >= 70:
        risk_label = "HIGH"
    elif risk_score >= 40:
        risk_label = "MEDIUM"
    else:
        risk_label = "LOW"
    lines.append(f"  Score: {risk_score}/100  --  {risk_label} RISK")
    lines.append("  Formula: (CRITICAL x 3) + (ERROR x 1), capped at 100")

    # Footer
    lines.append("\n" + "=" * 60)
    lines.append("  END OF REPORT - INFRALOG MONITOR")
    lines.append("=" * 60)

    return "\n".join(lines)


def save_report(parsed_report):
    content = build_report(parsed_report)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = REPORT_OUTPUT_DIR / f"report_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return filename, content


# ── Quick Test ───────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from parser.log_parser import parse_log_file

    logs = sorted(Path("logs/incoming").glob("*.log"))
    if not logs:
        print("No log files found. Run the generator first.")
        sys.exit(1)

    report = parse_log_file(logs[-1])
    filename, content = save_report(report)
    print(content)
    print(f"\nReport saved to: {filename}")