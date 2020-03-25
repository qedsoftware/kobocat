from functools import reduce, partial
from operator import add


mapc = lambda x: partial(map, x)

fst = lambda x: x[0]


def concat_map(f, iterable):
    return reduce(add, map(f, iterable), [])


def compose(*funcs):
    return reduce(lambda f, g: lambda *args: f(g(*args)), funcs, lambda x: x)


def merge_dicts(dict1, dict2):
    merged_dict = dict1.copy()
    merged_dict.update(dict2)
    return merged_dict
