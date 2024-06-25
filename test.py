import random


def return_call(ex, e):
    for i in ex:
        if isinstance(e, i[0]):
            return i[1]
    return None


def decorator(lis):
    def wrap(func1):
        def fun2(*args, **kwargs):
            try:
                func1(*args, **kwargs)
            except Exception as e:
                call = return_call(lis, e)
                if call is not None:
                    call()
        return fun2
    return wrap


def bar():
    print("1")


@decorator([(KeyError, bar), (IndexError, lambda: print("2"))])
def foo():
    if random.randint(1, 2) == 1:
        raise KeyError("bar")
    else:
        raise IndexError


foo()
