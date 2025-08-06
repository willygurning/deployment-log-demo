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

circleci_token = os.getenv('circle_ci_api_token', None)
workflow_id = os.getenv('CIRCLE_WORKFLOW_ID', '-')
if not circleci_token or not workflow_id:
    print("❌ API Token atau Workflow ID tidak tersedia")
    exit(1)

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

# 8. Cari baris berdasarkan workflow_id
cell = sheet.find(workflow_id)
if not cell:
    print("❌ Workflow ID tidak ditemukan di Google Sheet.")
    exit(1)

row_index = cell.row
# 8. Simpan data ke Google Sheet
status_info = []
for job in jobs:
    job_name = job.get("name", "-")
    status = job.get("status", "-")
    started_at = job.get("started_at")
    stopped_at = job.get("stopped_at")
    duration = calculate_duration(started_at, stopped_at) if started_at and stopped_at else "-"
    status_info.append(f"{job_name}: {status} ({duration})")
status_string = "\n".join(status_info)
sheet.update_cell(row_index, 8, status_string)

print("✅ Semua status job berhasil diupdate di baris yang sama.")
