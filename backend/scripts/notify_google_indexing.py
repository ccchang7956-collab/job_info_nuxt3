"""Preview or publish Google Indexing API notifications for active job IDs.

This command never sends notifications without --publish. It uses a read-only
SQLite connection, checks that the jobs are still open, and only sends
URL_UPDATED for job detail pages. It does not remove historical pages.
"""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPE = "https://www.googleapis.com/auth/indexing"


def active_notifications(db_path, job_ids, site_url, today=None):
    site_url = site_url.rstrip("/")
    parsed = urlsplit(site_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:
        raise ValueError("SITE_DOMAIN must be an HTTPS origin")
    ids = list(dict.fromkeys(job_ids))
    if not ids or len(ids) > 200 or any(job_id <= 0 for job_id in ids):
        raise ValueError("Supply 1–200 positive job IDs")
    today = today or datetime.now(ZoneInfo("Asia/Taipei"))
    roc_today = f"{today.year - 1911}{today:%m%d}"
    placeholders = ",".join("?" for _ in ids)
    with sqlite3.connect(Path(db_path).resolve().as_uri() + "?mode=ro", uri=True) as db:
        rows = db.execute(
            f"SELECT id FROM job_all_data WHERE id IN ({placeholders}) AND date_to >= ? ORDER BY id",
            [*ids, roc_today],
        ).fetchall()
    return [{"url": f"{site_url}/job/{row[0]}", "type": "URL_UPDATED"} for row in rows]


def publish_notifications(notifications, credentials_path):
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession

    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=[SCOPE])
    with AuthorizedSession(credentials) as session:
        for notification in notifications:
            response = session.post(ENDPOINT, json=notification, timeout=30)
            print(f"{notification['url']}: HTTP {response.status_code}")
            # Stop on auth, quota or server errors; do not burn the remaining quota.
            response.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(__file__).resolve().parents[1] / "database/data/job_info.db")
    parser.add_argument("--job-id", type=int, action="append", required=True)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    from dotenv import load_dotenv
    load_dotenv()
    notifications = active_notifications(args.db, args.job_id, os.getenv("SITE_DOMAIN", "https://opendgpa.shibaalin.com"))
    print(json.dumps({"mode": "publish" if args.publish else "preview", "notifications": notifications}, ensure_ascii=False, indent=2))
    if args.publish and notifications:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            parser.error("GOOGLE_APPLICATION_CREDENTIALS is required for --publish")
        publish_notifications(notifications, credentials_path)


if __name__ == "__main__":
    main()
