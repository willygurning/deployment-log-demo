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

    row = [
        timestamp,
        branch,
        status,
        job_name,
        author,
        build_url,
        commit
    ]
    sheet.append_row(row)

print("✅ Semua job deployment berhasil dicatat ke Google Sheets.")
