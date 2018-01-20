from functools import reduce
from operator import add


def id(x):
    return x


def concat_map(f, iterable):
    return reduce(add, map(f, iterable), [])


def compose(*funcs):
    return reduce(lambda f, g: lambda *args: f(g(*args)), funcs, id)


def remove_el(el, list):
    list.remove(el)
    return list


def merge_dicts(d1, d2):
    tmp = d1.copy()
    tmp.update(d2)
    return tmp
