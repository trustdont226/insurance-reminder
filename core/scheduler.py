"""
core/scheduler.py
Daily background job that identifies records whose insurance renewal falls
within the configured reminder window.

We don't auto-send messages here — Click-to-Chat requires a manual "Send" tap
in WhatsApp. The job just builds a "due list" that the agent can act on via
the "Send All Due Reminders" button in the UI.
"""

import json
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from core.config import TIMEZONE
from core.database import get_all_records, get_setting, set_setting


# ── Module-level scheduler instance ───────────────────────────────────────────

_scheduler = BackgroundScheduler(timezone=TIMEZONE)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_reminder_days() -> int:
    return int(get_setting("reminder_days", "3"))


# ── Job ───────────────────────────────────────────────────────────────────────

def run_scheduled_reminders():
    """Scan all records and persist a daily summary of who is due."""
    records = get_all_records()
    today = datetime.now().date()
    reminder_days = _get_reminder_days()
    due, skipped = [], []

    for rec in records:
        if rec.get("reminder_sent"):
            skipped.append(rec["id"])
            continue
        if not rec.get("mobile_number"):
            skipped.append(rec["id"])
            continue
        try:
            days = (datetime.strptime(rec["renewal_date"], "%d/%m/%Y").date() - today).days
        except (ValueError, TypeError):
            skipped.append(rec["id"])
            continue
        if not (0 <= days <= reminder_days):
            skipped.append(rec["id"])
            continue

        due.append(rec["id"])

    summary = json.dumps({"due": len(due), "skipped": len(skipped)})
    set_setting("scheduler_last_run",    datetime.now().strftime("%d/%m/%Y %H:%M"))
    set_setting("scheduler_last_result", summary)
    print(f"[Scheduler] Ran at {datetime.now().strftime('%H:%M')} — "
          f"Due:{len(due)} Skipped:{len(skipped)}")


# ── Public API used by app.py ─────────────────────────────────────────────────

def start():
    """Start the background scheduler (idempotent)."""
    if not _scheduler.running:
        _scheduler.start()


def apply_settings():
    """(Re)schedule or remove the daily job based on stored settings."""
    enabled  = get_setting("scheduler_enabled", "false") == "true"
    time_str = get_setting("scheduler_time", "09:00")

    try:
        hour, minute = map(int, time_str.split(":"))
    except ValueError:
        hour, minute = 9, 0

    if _scheduler.get_job("daily_reminders"):
        _scheduler.remove_job("daily_reminders")

    if enabled:
        _scheduler.add_job(
            run_scheduled_reminders,
            CronTrigger(hour=hour, minute=minute, timezone=TIMEZONE),
            id="daily_reminders",
            replace_existing=True,
        )
        print(f"[Scheduler] Enabled — runs daily at {hour:02d}:{minute:02d}")
    else:
        print("[Scheduler] Disabled")


def get_next_run_time():
    """Return next scheduled run time as a formatted string, or None."""
    job = _scheduler.get_job("daily_reminders")
    if job and job.next_run_time:
        return job.next_run_time.strftime("%d/%m/%Y %H:%M")
    return None
