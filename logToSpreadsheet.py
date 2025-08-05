import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timezone
import os
import json
import requests

# Load Google credentials dari environment
creds_dict = json.loads(os.environ['google_credentials'])

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Inisialisasi Google Sheet
spreadsheet = client.open("Deployment Quality Test")
sheet = spreadsheet.worksheet("DailyLog")

# Fungsi tunggu sampai workflow selesai
def get_final_workflow_status(workflow_id, token, max_wait_seconds=300, interval=5):
    url = f"https://circleci.com/api/v2/workflow/{workflow_id}"
    headers = {
        "Circle-Token": token
    }

    waited = 0
    while waited < max_wait_seconds:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Gagal mengambil status workflow: {response.text}")

        data = response.json()
        status = data.get("status", "unknown")

        if status in ["success", "failed", "error", "failing", "canceled", "unauthorized"]:
            return data

        print(f"🔄 Workflow masih {status}, tunggu {interval} detik...")
        time.sleep(interval)
        waited += interval

    raise TimeoutError(f"Workflow tidak selesai dalam {max_wait_seconds} detik.")

# Ambil data akhir workflow
workflow_data = get_final_workflow_status(workflow_id, circle_token)
# Ambil environment variables dari CircleCI
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

# Panggil CircleCI API untuk ambil semua job
url = f"https://circleci.com/api/v2/workflow/{workflow_id}/job"
headers = {
    "Circle-Token": circleci_token
}
response = requests.get(url, headers=headers)
response.raise_for_status()
jobs = response.json().get("items", [])

def calculate_duration(started_at, stopped_at):
    try:
        start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        stop = datetime.fromisoformat(stopped_at.replace("Z", "+00:00"))
        return str(stop - start)
    except:
        return "-"

# Tulis satu baris untuk setiap job dalam workflow
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

print("✅ Deployment job statuses successfully written to Google Sheets.")
