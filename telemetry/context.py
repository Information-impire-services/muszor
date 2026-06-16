import uuid
import time
from contextvars import ContextVar

from telemetry.bus import EventBus

current_context = ContextVar("current_context", default=None)


class ExecutionContext:
    def __init__(self, origin="http", trace_id=None, parent_span_id=None):
        self.trace_id = trace_id or uuid.uuid4().hex
        self.span_id = uuid.uuid4().hex
        self.parent_span_id = parent_span_id
        self.origin = origin
        self.start = time.time()
        self.events = []
        self.depth = 0

    def child(self):
        return ExecutionContext(
            origin=self.origin,
            trace_id=self.trace_id,
            parent_span_id=self.span_id,
        )

    def emit(self, event, **data):
        payload = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "event": event,
            "ts": time.time(),
            "origin": self.origin,
            "depth": self.depth,
            **data,
        }

        self.events.append(payload)
        EventBus.publish(payload)
        return payload


class lifecycle:
    def __enter__(self):
        self.ctx = ExecutionContext()
        current_context.set(self.ctx)
        self.ctx.emit("lifecycle.start")
        return self.ctx

    def __exit__(self, exc_type, exc, tb):
        self.ctx.emit("lifecycle.end", error=str(exc) if exc else None)


def get_current_context():
    return current_context.get()
