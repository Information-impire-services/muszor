import importlib
import inspect
import sys


def scan_module(module_name):
    module = importlib.import_module(module_name)

    found = []

    for name, obj in vars(module).items():
        if inspect.isfunction(obj):
            found.append((module_name, name, obj))

    return found