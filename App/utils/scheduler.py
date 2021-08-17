from threading import Thread
from time import sleep
from datetime import datetime, timedelta
from typing import Any, Optional, Callable, Dict

__all__ = (
    'Scheduler',
)


# TODO: допилить для проверки сессий и архивов


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

                if task is None or not task.active or now < task.next_time:
                    continue

                task.run()
                if task.is_single:
                    self.scheduler.tasks.pop(task_name, None)

            sleep(self.scheduler.period_s)


class SchedulerTask:
    __slots__ = (
        'name',
        'active',
        'is_single',
        'interval',
        'next_time',
        'func',
    )

    name: str
    active: bool
    is_single: bool
    interval: int
    next_time: Optional[datetime]
    func: Callable[[], Any]

    def __init__(self, name: str, active: bool, is_single: bool, interval: int,
                 func: Callable[[], Any]):
        """ Args:
              name: str,
              active: bool,
              is_single: bool,
              interval: seconds [int],
              func: () -> Any.
        """
        self.name = name
        self.active = active
        self.is_single = is_single
        self.interval = interval
        self.func = func

        if self.active:
            self.set_next_time()

    def set_next_time(self):
        self.next_time = datetime.now() + timedelta(seconds=self.interval)

    def run(self):
        try:
            result = self.func()
        except Exception as e:
            self._log_critical(f"{self.name} FAILED", e)
        else:
            self._log_info(f"{self.name} successfully completed ({result})")

        if self.is_single:
            self.active = False
        else:
            self.set_next_time()

    def activate(self, now: bool):
        self.active = True
        if now:
            self.next_time = datetime.now()
        else:
            self.set_next_time()

    def inactivate(self):
        self.active = False
        self.next_time = None

    @staticmethod
    def _log_info(text: str):
        print("SCHEDULER TASK", text)  # TODO: logger

    @staticmethod
    def _log_critical(text: str, ex: Exception):
        print("SCHEDULER TASK", text, ex)  # TODO: logger


class Scheduler:
    __slots__ = ('tasks', 'thread', 'period_s')

    tasks: Dict[str, SchedulerTask]  # name : SchedulerTask
    thread: Optional[SchedulerThread]

    def __init__(self, period_minutes: int):
        self.tasks = dict()
        self.thread = None
        self.period_s = period_minutes * 60

    def add(self, name: str, func: Callable[[], Any], interval_minutes: int, start_now: bool, single: bool):
        self.tasks[name] = SchedulerTask(
            name,
            start_now,
            single,
            interval_minutes * 60,
            func
        )

    def remove(self, name):
        self.tasks.pop(name, None)

    def run(self):
        self.thread = SchedulerThread(self)
        self.thread.start()

    def pause_task(self, name):
        """ Raises: KeyError """
        self.tasks[name].inactivate()

    def resume_task(self, name):
        """ Raises: KeyError """
        self.tasks[name].activate(True)

    def stop(self):
        self.thread.running = False
        self.thread.join()
