"""Daily update scheduler.

Re-crawls the help center on a schedule to keep the knowledge base fresh.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler

from config import settings

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def start_daily_update(crawl_and_index_fn):
    """Start the background scheduler for daily re-crawling.

    Args:
        crawl_and_index_fn: A callable that performs the full crawl + index.
    """
    global _scheduler

    if _scheduler is not None:
        logger.info("Scheduler already running")
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        crawl_and_index_fn,
        "interval",
        hours=settings.crawl_schedule_hours,
        id="daily_crawl",
        name="Daily help center re-crawl",
    )
    _scheduler.start()
    logger.info(
        "Scheduled daily re-crawl every %d hours",
        settings.crawl_schedule_hours,
    )


def stop_scheduler():
    """Shut down the scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
