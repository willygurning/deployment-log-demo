import requests
import gspread
from google.oauth2.service_account import Credentials

# --- Konfigurasi ---
CIRCLECI_TOKEN = ""
WORKFLOW_ID = "0a5adaf6-59a8-4c45-b180-cacd8f0e2802"
SPREADSHEET_ID = "15z2Dyl4k1OOobdU_54UqPrWCKmpPwfSe056NpyySoxQ"
SHEET_NAME = "Q3"

# --- Setup Google Sheets ---
creds = Credentials.from_service_account_file(
    '/Users/willyjemsgurning/Documents/google_credentials.json',
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# --- Panggil API CircleCI ---
url = f"https://circleci.com/api/v2/workflow/{WORKFLOW_ID}/job"
headers = {"Circle-Token": CIRCLECI_TOKEN}
response = requests.get(url, headers=headers)
data = response.json()

# --- Proses & Masukkan ke Sheet ---
for job in data.get("items", []):
    start_time = job.get("started_at", "")
    status = job.get("status", "")
    job_name = job.get("name", "")
    sheet.append_row([job_name, start_time, status])

print("Data dari CircleCI berhasil ditambahkan ke Google Sheets!")
