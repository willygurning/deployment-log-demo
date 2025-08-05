import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json
import requests
import time

# 1. Load Google credentials dari environment
creds_dict = json.loads(os.environ['google_credentials'])
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 2. Inisialisasi Google Sheet
spreadsheet = client.open("Deployment Quality Test")
sheet = spreadsheet.worksheet("DailyLog")

# 3. Ambil variabel dari environment
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
branch = os.getenv('CIRCLE_BRANCH', '-')
commit = os.getenv('CIRCLE_SHA1', '-')
workflow_id = os.getenv('CIRCLE_WORKFLOW_ID', '-')
project = os.getenv('CIRCLE_PROJECT_REPONAME', '-')
author = os.getenv('CIRCLE_USERNAME', '-')
build_url = os.getenv('CIRCLE_BUILD_URL', '-')
circleci_token = os.getenv('circle_ci_api_token', None)

if not circleci_token or not workflow_id:
    print("❌ API Token atau Workflow ID tidak tersedia")
    exit(1)

def get_final_workflow_status(workflow_id, circleci_token, max_retries=30, sleep_sec=5):
    headers = {
        "Circle-Token": circleci_token
    }

    url = f"https://circleci.com/api/v2/workflow/{workflow_id}"

    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers)
        data = resp.json()

        status = data.get("status")
        print(f"🔄 Status sekarang: {status} (percobaan ke-{attempt + 1})")

        if status in ("success", "failed", "error", "failing", "canceled", "unauthorized"):
            return data  # Status akhir ditemukan

        time.sleep(sleep_sec)

    print("⚠️ Timeout menunggu workflow selesai.")
    return {"status": "timeout"}

workflow_data = get_final_workflow_status(workflow_id, circleci_token)
workflow_status = workflow_data.get("status", "unknown")
# 6. Ambil data job dari API
url = f"https://circleci.com/api/v2/workflow/{workflow_id}/job"
headers = { "Circle-Token": circleci_token }
response = requests.get(url, headers=headers)
response.raise_for_status()
jobs = response.json().get("items", [])

# 7. Fungsi menghitung durasi job
def calculate_duration(started_at, stopped_at):
    try:
        start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        stop = datetime.fromisoformat(stopped_at.replace("Z", "+00:00"))
        return str(stop - start)
    except:
        return "-"

# 8. Simpan data ke Google Sheet
for job in jobs:
    job_name = job.get("name", "-")
    status = job.get("status", "-")
    started_at = job.get("started_at")
    stopped_at = job.get("stopped_at")
    duration = calculate_duration(started_at, stopped_at) if started_at and stopped_at else "-"

    row = [
        timestamp,
        branch,
        status,
        job_name,
        author,
        build_url,
        duration,
        project,
        commit
    ]
    sheet.append_row(row)

print("✅ Semua job deployment berhasil dicatat ke Google Sheets.")
