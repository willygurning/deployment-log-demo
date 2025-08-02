import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

# Load credentials dari environment variable
creds_dict = json.loads(os.environ['google_credentials'])

# Setup koneksi dengan Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Ganti ini dengan nama file dan sheet kamu
spreadsheet = client.open("Deployment Quality Test")
sheet = spreadsheet.worksheet("DailyLog")

# Ambil data dari environment CircleCI
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
branch = os.getenv('CIRCLE_BRANCH', '"-"')
status = os.getenv('DEPLOY_STATUS', 'unknown')  # set dari job sebelumnya
print("Status Deploy:", status)
job_name = os.getenv('CIRCLE_JOB', '"-"')
message = os.getenv('DEPLOY_MESSAGE', '')
author = os.getenv("CIRCLE_USERNAME", "-")
build_url = os.getenv("CIRCLE_BUILD_URL", "-")
error_message = os.getenv("DEPLOY_ERROR", "-")

# Tambahkan baris ke spreadsheet
row = [timestamp, branch, status, job_name, message, author, build_url, error_message]
sheet.append_row(row)

print("✅ Deployment log successfully written to Google Sheets.")
