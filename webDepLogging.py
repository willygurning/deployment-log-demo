import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timezone

# ==== CONFIGURATION ====
CIRCLECI_TOKEN = os.getenv("circle_ci_api_token") 
PROJECT_SLUG = "gh/oyindonesia/webrepo"
SPREADSHEET_NAME = "Deployment Quality Q3"

if not CIRCLECI_TOKEN:
    raise ValueError("CIRCLECI_TOKEN tidak ditemukan di environment variable.")

# ==== STEP 1: ambil workflow pipeline hari ini ====
def get_circleci_workflows_today():
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    url = f"https://circleci.com/api/v2/project/{PROJECT_SLUG}/pipeline"
    headers = {"Circle-Token": CIRCLECI_TOKEN}
    workflows_today = []

    while url:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        pipelines = data.get("items", [])

        for pipeline in pipelines:
            created_at = pipeline["created_at"][:10]
            branch = pipeline.get("vcs", {}).get("branch", "")

            # filter hanya master atau release/webrepo-YYYY-MM-DD
            if created_at == today_str and (branch == "master" or branch.startswith("release/webrepo-")):
                pipeline_id = pipeline["id"]
                workflow_url = f"https://circleci.com/api/v2/pipeline/{pipeline_id}/workflow"
                wf_res = requests.get(workflow_url, headers=headers)
                wf_res.raise_for_status()
                workflows = wf_res.json().get("items", [])

                for wf in workflows:
                    created = datetime.fromisoformat(wf["created_at"].replace("Z", "+00:00"))
                    stopped_str = wf.get("stopped_at")

                    if stopped_str:
                        stopped = datetime.fromisoformat(stopped_str.replace("Z", "+00:00"))
                        duration = round((stopped - created).total_seconds() / 60, 2)
                    else:
                        duration = "-"

                    workflows_today.append({
                        "pipeline_id": pipeline_id,
                        "workflow_id": wf["id"],
                        "branch": branch,
                        "name": wf["name"],
                        "status": wf["status"],
                        "created_at": wf["created_at"],
                        "stopped_at": wf.get("stopped_at") or "-",
                        "duration_minutes": duration
                    })

            elif created_at < today_str:
                return workflows_today

        # pagination kalau ada next page
        url = f"https://circleci.com/api/v2/project/{PROJECT_SLUG}/pipeline?page-token={data.get('next_page_token')}" \
            if data.get("next_page_token") else None

    return workflows_today

# ==== STEP 2: save ke Google Sheet (pakai env, bukan file) ====
def write_to_google_sheet(rows):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    google_credentials = os.getenv("google_credentials")
    if not google_credentials:
        raise ValueError("google_credentials tidak ditemukan di environment variable.")

    creds_dict = json.loads(google_credentials)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet("FE Deployment Daily Log")

    values = [
        [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data["pipeline_id"],
            data["workflow_id"],
            data["branch"],
            data["name"],
            data["status"],
            data["created_at"],
            data["stopped_at"],
            data["duration_minutes"]
        ]
        for data in rows
    ]

    if values:
        sheet.append_rows(values)  # bulk append

# ==== MAIN ====
if __name__ == "__main__":
    workflows_today = get_circleci_workflows_today()
    if workflows_today:
        write_to_google_sheet(workflows_today)
        print(f"{len(workflows_today)} workflows hari ini berhasil disimpan ke Google Sheet ✅")
    else:
        print("Tidak ada workflow ditemukan untuk hari ini.")
