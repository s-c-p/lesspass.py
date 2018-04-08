import inspect

def run_tests():
    fg = inspect.currentframe().f_back.f_globals
    g = list(fg.keys())
    for name in g:
        func = fg[name]
        if callable(func) and name.startswith("test"):
            print(name, end=" ")
            try:
                func()
            except Exception as e:
                print("failed", end="\n\t")
                print(repr(e))
            else:
                print("passed")