import json

def jsonl_sink(event):

    with open(
        "telemetry.jsonl",
        "a"
    ) as f:

        f.write(
            json.dumps(event)
            + "\n"
        )