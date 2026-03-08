"""
Heroku clock process — runs the temp_downloads purge once every 24 hours.

Add to Procfile:
    clock: python clock.py

This process runs independently of the bot worker, so the bot itself needs
no scheduler logic.
"""
from __future__ import annotations

import logging
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from cron.cleanup_temp import default_target, purge_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", hours=24, id="purge_temp_downloads")
def purge_temp_downloads() -> None:
    target = default_target()
    logging.info("Running scheduled purge of %s", target)
    try:
        removed = purge_all(target, dry_run=False)
        logging.info("Purge complete — %d item(s) removed", removed)
    except Exception:
        logging.exception("Scheduled purge failed")


if __name__ == "__main__":
    logging.info("Clock process started — purge scheduled every 24 hours")
    scheduler.start()
