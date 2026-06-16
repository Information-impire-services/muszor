from collections import defaultdict


class ExecutionGraphBuilder:
    def __init__(self):
        self.graph = defaultdict(list)

    def ingest(self, event):
        node = {
            "span_id": event.get("span_id"),
            "parent_span_id": event.get("parent_span_id"),
            "event": event.get("event"),
            "timestamp": event.get("ts"),
            "metadata": event,
        }

        self.graph[event["trace_id"]].append(node)

    def build_dag(self, trace_id):
        return self.graph.get(trace_id, [])