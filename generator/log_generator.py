import random
import time
from datetime import datetime
from pathlib import Path

# ── Config ──────────────────────────────────────────────────
LOG_OUTPUT_DIR = Path("logs/incoming")
LOG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SERVERS = [
    "web-server-01",
    "db-server-01",
    "api-gateway",
    "auth-server",
    "file-server",
]

# ── Event Templates ─────────────────────────────────────────

AUTH_EVENTS = [
    ("WARNING",  "Failed login attempt for user admin from {ip}"),
    ("WARNING",  "Failed login attempt for user root from {ip}"),
    ("CRITICAL", "Multiple failed logins detected from {ip} - possible brute force"),
    ("WARNING",  "Login attempt outside business hours by user {user}"),
    ("CRITICAL", "Unauthorized access attempt on restricted endpoint from {ip}"),
    ("INFO",     "Successful login by user {user} from {ip}"),
]

RESOURCE_EVENTS = [
    ("WARNING",  "CPU usage at {pct}% - approaching threshold"),
    ("CRITICAL", "CPU usage at {pct}% - threshold exceeded for 5+ minutes"),
    ("WARNING",  "Memory usage at {pct}% - monitor closely"),
    ("CRITICAL", "Memory usage at {pct}% - possible memory leak detected"),
    ("WARNING",  "Disk usage at {pct}% on /var/log partition"),
    ("CRITICAL", "Disk usage at {pct}% - write failures imminent"),
]

STABILITY_EVENTS = [
    ("ERROR",    "Service crashed unexpectedly - attempting restart"),
    ("WARNING",  "Service restarted {n} times in the last hour"),
    ("ERROR",    "API gateway timeout after 30s - downstream service unreachable"),
    ("CRITICAL", "Database connection pool exhausted - all requests failing"),
    ("ERROR",    "HTTP 500 error rate at {pct}% over last 10 minutes"),
    ("INFO",     "Service health check passed - all systems normal"),
]

# ── Helpers ──────────────────────────────────────────────────

def random_ip():
    return f"{random.randint(10,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def random_user():
    return random.choice(["jsmith", "adavis", "mlopez", "rthomas", "unknown_user"])

def random_pct(low, high):
    return random.randint(low, high)

def generate_event(category):
    server = random.choice(SERVERS)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if category == "auth":
        severity, template = random.choice(AUTH_EVENTS)
        message = template.format(ip=random_ip(), user=random_user())
    elif category == "resource":
        severity, template = random.choice(RESOURCE_EVENTS)
        message = template.format(pct=random_pct(75, 99), n=random.randint(2, 10))
    else:
        severity, template = random.choice(STABILITY_EVENTS)
        message = template.format(pct=random_pct(10, 60), n=random.randint(2, 10))

    return f"{timestamp} | {severity:<8} | {server:<15} | {message}"

# ── Main Generator ───────────────────────────────────────────

def generate_log_file(num_events=50):
    filename = LOG_OUTPUT_DIR / f"server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    categories = ["auth", "resource", "stability"]

    with open(filename, "w") as f:
        for _ in range(num_events):
            category = random.choice(categories)
            line = generate_event(category)
            f.write(line + "\n")

    print(f"[+] Generated log file: {filename} ({num_events} events)")
    return filename

if __name__ == "__main__":
    print("[*] Starting log generator - press Ctrl+C to stop\n")
    try:
        while True:
            generate_log_file(num_events=random.randint(30, 80))
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[*] Generator stopped")