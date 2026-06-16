from telemetry.sink import console_sink


class EventBus:
    subscribers = []

    @classmethod
    def init(cls):
        # ensure default sink exists
        if console_sink not in cls.subscribers:
            cls.subscribers.append(console_sink)

    @classmethod
    def publish(cls, event):
        for sub in list(cls.subscribers):
            sub(event)

    @classmethod
    def subscribe(cls, fn):
        cls.subscribers.append(fn)


# initialize default sink
EventBus.init()
from telemetry.storage import jsonl_sink
from telemetry.graph_runtime import graph_builder

EventBus.subscribe(jsonl_sink)
EventBus.subscribe(graph_builder.ingest)