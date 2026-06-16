from telemetry.bus import EventBus

def console_sink(event):
    print("[TRACE]", event)

EventBus.subscribe(console_sink)
