from App.database import DbUtils
from App.utils.logging import LoggerFactory
from threading import Thread, Event
from datetime import datetime, timedelta
from typing import Any, Optional, Callable, Dict, Coroutine
import asyncio

__all__ = (
    'Scheduler',
    'SchedulerTask',
)


class SchedulerThread(Thread):
    def __init__(self, scheduler: 'Scheduler'):
        super().__init__(daemon=True)
        self._scheduler = scheduler
        self._stop_event = Event()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        db_utils = DbUtils(1)
        loop.run_until_complete(db_utils.init())

        self._stop_event.clear()
        while not self._stop_event.is_set():
            self.sleeping = False
            now = datetime.now()

            for task_name in tuple(self._scheduler.tasks.keys()):
                task = self._scheduler.tasks.get(task_name)

                if task is None or not task.is_active or now < task.next_time:
                    continue

                loop.run_until_complete(task.run(SchedulerTask.Context(db_utils)))

                if task.is_single:
                    self._scheduler.tasks.pop(task_name, None)

            self._stop_event.wait(self._scheduler.period_s)

        loop.run_until_complete(db_utils.dispose())

    def stop(self):
        self._stop_event.set()


class SchedulerTask:
    __slots__ = (
        'name',
        'is_active',
        'is_single',
        'interval_s',
        'func',
        'next_time',
    )

    logger = LoggerFactory.get_named("SCHEDULER TASK")

    def __init__(self, name: str, active: bool, single: bool, interval_minutes: int,
                 start_now: bool, func: Callable[['SchedulerTask.Context'], Any]):
        self.name: str = name
        self.is_active: bool = active
        self.is_single: bool = single
        self.interval_s: int = interval_minutes * 60
        self.func: Callable[['SchedulerTask.Context'], Coroutine] = func
        self.next_time: Optional[datetime] = None

        if self.is_active:
            self.set_next_time(start_now)

    def set_next_time(self, now: bool = False):
        if now:
            self.next_time = datetime.now()
        else:
            self.next_time = datetime.now() + timedelta(seconds=self.interval_s)

    async def run(self, db: 'SchedulerTask.Context'):
        try:
            result = await self.func(db)
        except Exception as ex:
            self.logger.critical("{0} failed", self.name, ex=ex)
        else:
            if result is None:
                self.logger.info("{0} successfully completed", self.name)
            else:
                self.logger.info("{0} successfully completed ({1})", self.name, result)

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

    class Context:
        __slots__ = ('db_utils', )

        def __init__(self, db_utils: DbUtils):
            self.db_utils = db_utils


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
        self.thread.stop()
        self.thread.join()
        self.thread = None
