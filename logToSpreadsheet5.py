import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timezone

# ==== CONFIGURATION ====
CIRCLECI_TOKEN = ""
PROJECT_SLUG = "gh/willygurning/deployment-log-demo"
BRANCH = "main"
SPREADSHEET_NAME = "Deployment Quality Test"

# ==== STEP 1: Ambil semua pipeline untuk hari ini ====
def get_circleci_workflows_today():
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    url = f"https://circleci.com/api/v2/project/{PROJECT_SLUG}/pipeline?branch={BRANCH}"
    headers = {"Circle-Token": CIRCLECI_TOKEN}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    pipelines = res.json().get("items", [])

    workflows_today = []

    for pipeline in pipelines:
        created_at = pipeline["created_at"][:10]  # format YYYY-MM-DD
        if created_at != today_str:
            continue  # skip kalau bukan hari ini

        pipeline_id = pipeline["id"]
        workflow_url = f"https://circleci.com/api/v2/pipeline/{pipeline_id}/workflow"
        wf_res = requests.get(workflow_url, headers=headers)
        wf_res.raise_for_status()
        workflows = wf_res.json().get("items", [])

        for wf in workflows:
            workflows_today.append({
                "pipeline_id": pipeline_id,
                "workflow_id": wf["id"],
                "name": wf["name"],
                "status": wf["status"],
                "created_at": wf["created_at"],
                "stopped_at": wf.get("stopped_at") or "-"
            })

    return workflows_today

# ==== STEP 2: Simpan ke Google Sheet ====
def write_to_google_sheet(rows):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "/Users/willyjemsgurning/Documents/google_credentials.json", scope
    )
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet("Q3")

    for data in rows:
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data["pipeline_id"],
            data["workflow_id"],
            data["name"],
            data["status"],
            data["created_at"],
            data["stopped_at"]
        ])

# ==== MAIN ====
if __name__ == "__main__":
    workflows_today = get_circleci_workflows_today()
    if workflows_today:
        write_to_google_sheet(workflows_today)
        print(f"{len(workflows_today)} data workflow berhasil dicatat ke Google Sheet.")
    else:
        print("Tidak ada workflow hari ini.")
