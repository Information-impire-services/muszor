import sys
from telemetry.scanner import scan_module
from telemetry.context import current_context


def trace(name):
    def wrapper(fn):
        def inner(*args, **kwargs):
            ctx = current_context.get()
            if ctx:
                ctx.emit("function.enter", name=name)

            try:
                result = fn(*args, **kwargs)

                if ctx:
                    ctx.emit("function.exit", name=name)

                return result

            except Exception as e:
                if ctx:
                    ctx.emit("function.error", name=name, error=str(e))
                raise

        return inner
    return wrapper


def instrument_module(module_name):
    discovered = scan_module(module_name)

    module = sys.modules[module_name]

    for mod, name, fn in discovered:
        wrapped = trace(f"{mod}.{name}")(fn)
        setattr(module, name, wrapped)


def auto_instrument(*modules):
    for m in modules:
        instrument_module(m)