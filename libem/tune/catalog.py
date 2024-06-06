import os
import shelve

_dir = os.path.dirname(os.path.abspath(__file__))
_db_file = os.path.join(_dir, 'catalog.db')


def save(params):
    catalog = shelve.open(_db_file, writeback=True)
    catalog.update(params)
    catalog.close()


def load():
    catalog = shelve.open(_db_file, writeback=True)
    return catalog
