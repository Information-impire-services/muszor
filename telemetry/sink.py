import json


def console_sink(event):
    trace = event.get("trace_id", "no-trace")[:8]
    name = event.get("event", "unknown")

    extras = {k: v for k, v in event.items() if k not in ("trace_id", "event", "ts")}

    line = f"[TRACE {trace}] {name}"

    if extras:
        line += " | " + json.dumps(extras)

    print(line)