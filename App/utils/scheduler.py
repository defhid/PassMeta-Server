from threading import Thread
from time import sleep
from datetime import datetime, timedelta
from typing import Any, Optional, Callable, Dict
import traceback
import logging

__all__ = (
    'Scheduler',
    'SchedulerTask',
)

logger = logging.getLogger(__name__)


class SchedulerThread(Thread):
    def __init__(self, scheduler: 'Scheduler'):
        super().__init__()
        self.scheduler = scheduler
        self.running = False
        self.daemon = True

    def run(self):
        self.running = True
        while self.running:
            now = datetime.now()

            for task_name in tuple(self.scheduler.tasks.keys()):
                task = self.scheduler.tasks.get(task_name)

                if task is None or not task.is_active or now < task.next_time:
                    continue

                task.run()
                if task.is_single:
                    self.scheduler.tasks.pop(task_name, None)

            sleep(self.scheduler.period_s)


class SchedulerTask:
    __slots__ = (
        'name',
        'is_active',
        'is_single',
        'interval_s',
        'func',
        'next_time',
    )

    def __init__(self, name: str, active: bool, single: bool, interval_minutes: int,
                 start_now: bool, func: Callable[[], Any]):
        self.name: str = name
        self.is_active: bool = active
        self.is_single: bool = single
        self.interval_s: int = interval_minutes * 60
        self.func: Callable[[], Any] = func
        self.next_time: Optional[datetime] = None

        if self.is_active:
            self.set_next_time(start_now)

    def set_next_time(self, now: bool = False):
        if now:
            self.next_time = datetime.now()
        else:
            self.next_time = datetime.now() + timedelta(seconds=self.interval_s)

    def run(self):
        try:
            result = self.func()
        except Exception as e:
            self._log_critical(f"{self.name} FAILED", e)
        else:
            self._log_info(f"{self.name} successfully completed ({result})")

        if self.is_single:
            self.is_active = False
        else:
            self.set_next_time(False)

    def activate(self, now: bool):
        self.is_active = True
        self.set_next_time(now)

    def inactivate(self):
        self.is_active = False
        self.next_time = None

    @staticmethod
    def _log_info(text: str):
        logger.info("SCHEDULER TASK: " + text)

    @staticmethod
    def _log_critical(text: str, ex: Exception):
        logger.critical("SCHEDULER TASK: " + text, ex)


class Scheduler:
    __slots__ = ('tasks', 'thread', 'period_s')

    def __init__(self, period_minutes: int):
        self.tasks: Dict[str, SchedulerTask] = dict()
        self.thread: Optional[SchedulerThread] = None
        self.period_s = period_minutes * 60

    def add(self, task: SchedulerTask):
        self.tasks[task.name] = task

    def remove(self, name: str):
        self.tasks.pop(name, None)

    def run(self):
        self.thread = SchedulerThread(self)
        self.thread.start()

    def pause_task(self, name: str):
        """ Raises: KeyError """
        self.tasks[name].inactivate()

    def resume_task(self, name: str, start_now: bool):
        """ Raises: KeyError """
        self.tasks[name].activate(start_now)

    def stop(self):
        self.thread.running = False
        self.thread.join()
