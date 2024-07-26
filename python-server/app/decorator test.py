def decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Decorating function: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@decorator
def func_gay():
    print('Hello')

func_gay()
