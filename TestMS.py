from langgraph.checkpoint import MemorySaver

methods_list = [method for method in dir(MemorySaver()) if callable(
    getattr(MemorySaver(), method)) and not method.startswith("__")]


print(methods_list)
