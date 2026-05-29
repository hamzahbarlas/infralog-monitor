# ── Base Image ───────────────────────────────────────────────
FROM python:3.12-slim

# ── Set Working Directory ────────────────────────────────────
WORKDIR /app

# ── Install Dependencies ─────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy Project Files ───────────────────────────────────────
COPY generator/ ./generator/
COPY parser/ ./parser/
COPY reporter/ ./reporter/
COPY watcher/ ./watcher/
COPY notifier/ ./notifier/
COPY azure/ ./azure/
COPY config/ ./config/

# ── Create Log Directories ───────────────────────────────────
RUN mkdir -p logs/incoming logs/reports

# ── Default Command ──────────────────────────────────────────
CMD ["python", "watcher/file_watcher.py"]