import numpy as np

def bar():
    print(2//0)

def foo():
    bar()

foo()
