import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==== CONFIGURATION ====
CIRCLECI_TOKEN = ""  # Token API CircleCI
PROJECT_SLUG = "gh/willygurning/deployment-log-demo"  # format: gh/org-name/repo-name
BRANCH = "main"  # Nama branch yang ingin dilihat
SPREADSHEET_NAME = "Deployment Quality Test"  # Nama Google Sheet

# ==== STEP 1: Ambil data dari CircleCI API ====
def get_circleci_workflow_data():
    url = f"https://circleci.com/api/v2/project/{PROJECT_SLUG}/pipeline?branch={BRANCH}"
    headers = {"Circle-Token": CIRCLECI_TOKEN}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    pipelines = res.json().get("items", [])

    if not pipelines:
        return None

    # Ambil pipeline paling baru
    pipeline_id = pipelines[0]["id"]

    # Ambil workflow untuk pipeline ini
    workflow_url = f"https://circleci.com/api/v2/pipeline/{pipeline_id}/workflow"
    wf_res = requests.get(workflow_url, headers=headers)
    wf_res.raise_for_status()
    workflows = wf_res.json().get("items", [])

    if workflows:
        wf = workflows[0]
        return {
            "pipeline_id": pipeline_id,
            "workflow_id": wf["id"],
            "name": wf["name"],
            "status": wf["status"],
            "created_at": wf["created_at"],
            "stopped_at": wf.get("stopped_at")
        }
    return None

# ==== STEP 2: Simpan ke Google Sheet ====
def write_to_google_sheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/willyjemsgurning/Documents/google_credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open(SPREADSHEET_NAME).worksheet("Q3")
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data["pipeline_id"],
        data["workflow_id"],
        data["name"],
        data["status"],
        data["created_at"],
        data["stopped_at"] or "-"
    ])

# ==== MAIN ====
if __name__ == "__main__":
    workflow_data = get_circleci_workflow_data()
    if workflow_data:
        write_to_google_sheet(workflow_data)
        print("Data berhasil dicatat ke Google Sheet.")
    else:
        print("Tidak ada data workflow ditemukan.")
