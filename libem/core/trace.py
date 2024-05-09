class Trace:
    """Collects a trace of structured outputs"""

    def __init__(self):
        self.trace = []
        self.history = []

    def __enter__(self):
        """Enter the tracing context."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the tracing context."""
        self.stop()

    def start(self):
        """Starts tracing."""
        self.reset()
        return self

    def reset(self):
        # At any point in time, self.trace and self.history
        # together should contain the complete traces.
        self.history.append(self.trace)
        self.trace = []
        return self

    def stop(self):
        """Stops tracing."""
        return self

    def add(self, span):
        """Starts tracing."""
        self.trace.append(span)
        return self

    def get(self):
        # Return the trace in reverse / stack order
        return self.trace[::-1]

    def get_history(self):
        return self.history


"""A global tracer object that libem tools reports to."""
trace = Trace().start()
