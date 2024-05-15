class Telemetry:
    def __init__(self):
        self.telemetry = []
        self.history = []

    def __enter__(self):
        """Enter the telemetry context."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the telemetry context."""
        self.stop()

    def start(self):
        """Starts tracing."""
        self.reset()
        return self

    def reset(self):
        self.history.append(self.telemetry)
        self.telemetry = []
        return self

    def stop(self):
        return self

    def add(self, report):
        self.telemetry.append(report)
        return self

    def get(self):
        # Return the trace in reverse / stack order
        return self.telemetry

    def get_history(self):
        return self.history


"""A global telemetry object that libem tools reports to."""
telemetry = Telemetry().start()
