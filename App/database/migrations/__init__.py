from App.database.migrations.base import BaseMigration

import pkgutil as __pkgutil
import inspect as __inspect
import re as __re


def __load_migrations():
    loaded = []
    for loader, module_name, is_pkg in __pkgutil.walk_packages(__path__):
        if __re.fullmatch(r'^\d\d\d\d_\d\d_\d\d__\d\d+$', module_name):
            module = loader.find_module(module_name).load_module(module_name)
            for name, value in __inspect.getmembers(module, __inspect.isclass):
                if issubclass(value, BaseMigration) and value is not BaseMigration:
                    loaded.append(value)
    return loaded


MIGRATIONS = __load_migrations()

__all__ = ('MIGRATIONS', )
