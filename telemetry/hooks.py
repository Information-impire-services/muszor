import asyncio
import uuid
from telemetry.context import current_context


_original_create_task = asyncio.create_task


def install_async_hooks():
    def wrapped(coro, *args, **kwargs):
        ctx = current_context.get()
        span_id = uuid.uuid4().hex

        if ctx:
            ctx.emit("async.task.spawn", span_id=span_id)

        try:
            return _original_create_task(coro, *args, **kwargs)
        except TypeError:
            # Fallback for Python versions where create_task doesn't accept
            # some kwargs (e.g., name or context). Try to preserve behavior
            # without raising: create the task and then apply name or
            # create it under the provided context if possible.
            kw = dict(kwargs)
            context_obj = kw.pop("context", None)
            name = kw.pop("name", None)

            if context_obj is not None:
                def _make_task():
                    return _original_create_task(coro)

                try:
                    task = context_obj.run(_make_task)
                except Exception:
                    task = _original_create_task(coro)
            else:
                task = _original_create_task(coro)

            if name is not None:
                try:
                    task.set_name(name)
                except Exception:
                    pass

            return task

    asyncio.create_task = wrapped