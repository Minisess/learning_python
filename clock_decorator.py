import time
import functools


class Clock(object):
    """
    This is a decorator for the purpose of timing
    functions and classes, it can be added to any function
    and during runtime will spit out a formatted str
    that displays function(arguments) and results with
    a time delta. Uses pref_counter() not time()
    """
    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        t0 = time.perf_counter()
        result = self.func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        name = self.func.__name__
        arg_lst = []
        if args:
            arg_lst.extend(repr(arg) for arg in args)
        if kwargs:
            arg_lst.extend('{}={}'.format(k, w) for k, w in kwargs.items())
        arg_str = (', '.join(arg_lst))
        print('TIME TRIAL: {:s}({:.30s}~) -> {!r:.30}~ dt=[{:.8}]'.format(name, arg_str, result, elapsed))
        print()
        return result


@Clock
def list_combine(list1: list, list2: list):
    listx = []
    listx.extend(repr(x) for x in list1)
    listx.extend(repr(x) for x in list2)
    arg_str = ', '.join(listx)
    return arg_str


@Clock
def list_combine1(list1: list, list2: list):
    listx = []
    for x in list1:
        listx.append(repr(x))
    for x in list2:
        listx.append(repr(x))
    arg_str = ', '.join(listx)
    return arg_str


@Clock
def list_combine2(list1: list, list2: list):
    listx = []
    listx.append(', '.join(repr(x) for x in list1))
    listx.append(', '.join(repr(y) for y in list2))
    arg_str = ', '.join(listx)
    return arg_str


list1 = [1, 2, 3, 4, 5]
list2 = ['taco', 'banana', 'pizza']

print(list_combine(list1, list2))
print(list_combine1(list1, list2))
print(list_combine2(list1, list2))