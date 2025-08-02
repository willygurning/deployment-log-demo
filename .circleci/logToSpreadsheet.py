import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Inisialisasi koneksi ke Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("circleci-logger-5cab946cfc5c.json", scope)
client = gspread.authorize(creds)

# Buka spreadsheet dan worksheet
spreadsheet = client.open_by_key("15z2Dyl4k1OOobdU_54UqPrWCKmpPwfSe056NpyySoxQ")
worksheet = spreadsheet.worksheet("Daily Log")  # Ganti sesuai nama sheet/tab kamu

# Data log deployment
deployment_data = [
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
    "Payment Service",                             # Nama service
    "Success",                                     # Status deployment: Success / Failed / Hotfix
    "No issue detected"                            # Keterangan tambahan
]

# Tambahkan ke baris paling bawah (append)
worksheet.append_row(deployment_data)

print("Log deployment berhasil ditambahkan!")
