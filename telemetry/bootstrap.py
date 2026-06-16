from telemetry.bus import EventBus
from telemetry.sink import console_sink
from telemetry.storage import jsonl_sink
from telemetry.graph_runtime import graph_builder

def bootstrap():
    EventBus.subscribe(console_sink)
    EventBus.subscribe(jsonl_sink)
    EventBus.subscribe(graph_builder.ingest)