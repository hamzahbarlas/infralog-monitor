import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "infralog-archive")

# ── Uploader ─────────────────────────────────────────────────

def upload_to_blob(filepath, subfolder="logs"):
    if not CONNECTION_STRING:
        print("[-] No Azure connection string found in .env")
        return False, "No connection string"

    try:
        blob_service = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        container = blob_service.get_container_client(CONTAINER_NAME)

        filename = Path(filepath).name
        timestamp = datetime.now().strftime("%Y/%m/%d")
        blob_name = f"{subfolder}/{timestamp}/{filename}"

        with open(filepath, "rb") as f:
            container.upload_blob(blob_name, f, overwrite=True)

        blob_url = f"https://infraloglogs.blob.core.windows.net/{CONTAINER_NAME}/{blob_name}"
        return True, blob_url

    except Exception as e:
        return False, str(e)


# ── Quick Test ───────────────────────────────────────────────

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent))
    from parser.log_parser import parse_log_file
    from reporter.report_builder import save_report

    logs = sorted(Path("logs/incoming").glob("*.log"))
    if not logs:
        print("No log files found. Run the generator first.")
        sys.exit(1)

    # Upload a log file
    print(f"Uploading log file: {logs[-1].name}")
    success, result = upload_to_blob(logs[-1], subfolder="logs")
    if success:
        print(f"[+] Log uploaded: {result}")
    else:
        print(f"[-] Upload failed: {result}")

    # Upload a report file
    reports = sorted(Path("logs/reports").glob("*.txt"))
    if reports:
        print(f"\nUploading report: {reports[-1].name}")
        success, result = upload_to_blob(reports[-1], subfolder="reports")
        if success:
            print(f"[+] Report uploaded: {result}")
        else:
            print(f"[-] Upload failed: {result}")