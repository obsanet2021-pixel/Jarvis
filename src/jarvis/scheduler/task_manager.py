"""Task scheduler for JARVIS background jobs."""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    """A scheduled task in JARVIS."""

    id: str
    name: str
    callback: Callable[..., Any]
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    interval: float | None = None  # None = one-time
    delay: float = 0.0
    enabled: bool = True
    last_run: float | None = None
    next_run: float = field(default_factory=lambda: time.time())
    run_count: int = 0
    max_runs: int | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "interval": self.interval,
            "delay": self.delay,
            "enabled": self.enabled,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "run_count": self.run_count,
            "max_runs": self.max_runs,
        }


class TaskManager:
    """Manages scheduled and recurring tasks."""

    def __init__(self) -> None:
        self._tasks: Dict[str, ScheduledTask] = {}
        self._lock = threading.RLock()
        self._running = False
        self._thread: threading.Thread | None = None

    def schedule(
        self,
        name: str,
        callback: Callable[..., Any],
        *,
        interval: float | None = None,
        delay: float = 0.0,
        max_runs: int | None = None,
        args: tuple = (),
        kwargs: dict | None = None,
    ) -> ScheduledTask:
        """Schedule a new task."""
        task = ScheduledTask(
            id=str(uuid.uuid4())[:8],
            name=name,
            callback=callback,
            args=args,
            kwargs=kwargs or {},
            interval=interval,
            delay=delay,
            next_run=time.time() + delay,
            max_runs=max_runs,
        )
        with self._lock:
            self._tasks[task.id] = task
        logger.info("Scheduled task: %s (%s)", name, task.id)
        return task

    def cancel(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
        return False

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[ScheduledTask]:
        """List all tasks."""
        with self._lock:
            return list(self._tasks.values())

    def enable(self, task_id: str) -> bool:
        """Enable a task."""
        task = self._tasks.get(task_id)
        if task:
            task.enabled = True
            return True
        return False

    def disable(self, task_id: str) -> bool:
        """Disable a task."""
        task = self._tasks.get(task_id)
        if task:
            task.enabled = False
            return True
        return False

    def start(self) -> None:
        """Start the task manager."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("Task manager started")

    def stop(self) -> None:
        """Stop the task manager."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        logger.info("Task manager stopped")

    def _loop(self) -> None:
        """Main task processing loop."""
        while self._running:
            now = time.time()
            with self._lock:
                tasks = list(self._tasks.values())

            for task in tasks:
                if not task.enabled:
                    continue
                if task.next_run <= now:
                    self._execute_task(task)

            time.sleep(0.5)

    def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a single task."""
        try:
            task.callback(*task.args, **task.kwargs)
            task.last_run = time.time()
            task.run_count += 1

            if task.interval is not None:
                task.next_run = time.time() + task.interval
            else:
                task.enabled = False  # One-time task done

            if task.max_runs and task.run_count >= task.max_runs:
                task.enabled = False
                logger.info("Task %s reached max runs, disabling", task.name)

        except Exception as exc:
            logger.error("Task %s failed: %s", task.name, exc)


__all__ = ["TaskManager", "ScheduledTask"]