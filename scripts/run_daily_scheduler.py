from __future__ import annotations

import argparse
from datetime import date

from app.db.session import SessionLocal
from app.services.scheduling.daily import DailyProductionScheduler


def main() -> None:
    parser = argparse.ArgumentParser(description="Create idempotent daily AI content generation jobs")
    parser.add_argument("--organization-id", required=True)
    parser.add_argument("--day", default=date.today().isoformat())
    args = parser.parse_args()

    day = date.fromisoformat(args.day)
    with SessionLocal() as db:
        jobs = DailyProductionScheduler().plan_organization_day(db, args.organization_id, day)
        print(f"planned {len(jobs)} daily generation jobs for {args.organization_id} on {day}")


if __name__ == "__main__":
    main()
