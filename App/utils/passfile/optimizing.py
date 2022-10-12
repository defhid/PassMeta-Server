from datetime import date
from itertools import groupby
from typing import List, Set
from App.database import PassFileVersion

__all__ = (
    'ExcessVersionsFinder',
)


class ExcessVersionsFinder:
    def __init__(self, keep_versions: int, keep_day_versions: int):
        self.keep_versions = max(keep_versions, 0)
        self.keep_day_versions = max(keep_day_versions, 1)

    def find(self, sorted_versions: List[PassFileVersion]) -> Set[PassFileVersion]:
        """
        1) Current day: keep the oldest and the newest versions.
        2) Previous days: keep the newest versions, one a day.
        :param sorted_versions: Versions sorted by ascending.
        :return: Versions to delete.
        """

        to_delete = set()

        if not sorted_versions:
            return to_delete

        grouped = [(x[0], list(x[1])) for x in groupby(sorted_versions, key=lambda x: x.version_date.date())]

        if grouped[-1][0] == date.today():
            today_versions = grouped.pop(-1)[1]

            if len(today_versions) >= self.keep_day_versions:
                to_delete_today = len(today_versions) - self.keep_day_versions + 1

                for i in range(1, min(to_delete_today + 1, len(today_versions) - 1)):
                    to_delete.add(today_versions[i])

                if len(to_delete) < to_delete_today:
                    to_delete.add(today_versions[0])

                if len(to_delete) < to_delete_today:
                    to_delete.add(today_versions[-1])

        less_priority = set()
        total = 0

        for _, group in grouped:
            total += len(group)
            for i in range(len(group) - 1):
                less_priority.add(group[i])

        for _ in range(min(len(less_priority), total - self.keep_versions)):
            to_delete.add(less_priority.pop())
            total -= 1

        if total > self.keep_versions:
            k = 0
            for _, group in reversed(grouped):
                for version in reversed(group):
                    if version in to_delete:
                        continue
                    elif k < self.keep_versions:
                        k += 1
                    else:
                        to_delete.add(version)

        return to_delete
