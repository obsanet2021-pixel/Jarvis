"""Background job management for JARVIS."""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Status of a background job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackgroundJob:
    """A background job in JARVIS."""

    id: str
    name: str
    status: JobStatus = JobStatus.PENDING
    result: Any = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None


class BackgroundJobManager:
    """Manages background jobs with a thread pool."""

    def __init__(self, max_workers: int = 4) -> None:
        self._max_workers = max_workers
        self._jobs: Dict[str, BackgroundJob] = {}
        self._lock = threading.RLock()
        self._running = False
        self._threads: List[threading.Thread] = []

    def submit(
        self,
        name: str,
        func: Callable[..., Any],
        args: tuple = (),
        kwargs: dict | None = None,
    ) -> BackgroundJob:
        """Submit a background job."""
        import uuid

        job = BackgroundJob(
            id=str(uuid.uuid4())[:8],
            name=name,
        )
        with self._lock:
            self._jobs[job.id] = job

        if self._running:
            self._run_job(job, func, args, kwargs or {})
        else:
            job.error = "Job manager not running"

        return job

    def start(self) -> None:
        """Start the job manager."""
        self._running = True
        logger.info("Background job manager started")

    def stop(self) -> None:
        """Stop the job manager."""
        self._running = False
        for t in self._threads:
            t.join(timeout=1.0)
        self._threads.clear()
        logger.info("Background job manager stopped")

    def _run_job(
        self,
        job: BackgroundJob,
        func: Callable,
        args: tuple,
        kwargs: dict,
    ) -> None:
        """Run a job in a background thread."""

        def worker():
            job.status = JobStatus.RUNNING
            job.started_at = time.time()
            try:
                job.result = func(*args, **kwargs)
                job.status = JobStatus.COMPLETED
            except Exception as exc:
                job.error = str(exc)
                job.status = JobStatus.FAILED
                logger.error("Job %s failed: %s", job.name, exc)
            finally:
                job.completed_at = time.time()

        t = threading.Thread(target=worker, daemon=True)
        with self._lock:
            self._threads.append(t)
        t.start()

    def get_job(self, job_id: str) -> Optional[BackgroundJob]:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    def list_jobs(self) -> List[BackgroundJob]:
        """List all jobs."""
        with self._lock:
            return list(self._jobs.values())

    def get_active_jobs(self) -> List[BackgroundJob]:
        """Get currently running jobs."""
        with self._lock:
            return [j for j in self._jobs.values() if j.status == JobStatus.RUNNING]


__all__ = ["BackgroundJobManager", "BackgroundJob", "JobStatus"]