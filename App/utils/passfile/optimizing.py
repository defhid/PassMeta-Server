from datetime import date
from itertools import groupby
from math import ceil
from typing import List, Set
from App.database import PassFileVersion

__all__ = (
    'ExcessVersionsFinder',
)


class ExcessVersionsFinder:
    def __init__(self, keep_versions: int, keep_day_versions: int):
        self.keep_versions = keep_versions
        self.keep_day_versions = keep_day_versions

    def find(self, sorted_versions: List[PassFileVersion]) -> Set[PassFileVersion]:
        to_delete = set()

        if not sorted_versions:
            return to_delete

        grouped = [(x[0], list(x[1])) for x in groupby(sorted_versions, key=lambda x: x.version_date.date())]

        if grouped[-1][0] == date.today():
            today_versions = list(grouped.pop(-1)[1])

            if len(today_versions) >= self.keep_day_versions:
                k = ceil((len(today_versions) + 1) / self.keep_day_versions)

                for i in range(len(today_versions)):
                    if i % k != 0:
                        to_delete.add(today_versions[i])

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
