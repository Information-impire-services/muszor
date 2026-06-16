import os

class TelemetryConfig:
    def __init__(self):
        self.mode = os.getenv("TELEMETRY_MODE", "console")
        self.service_name = os.getenv("SERVICE_NAME", "audio-pipeline")
        self.enable_colors = True
        self.verbose = True

config = TelemetryConfig()