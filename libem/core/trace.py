import libem
from libem.tune.optimize.cost import openai


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

    def stats(self):
        trace = self.get()
        latencies = []
        num_model_calls, num_input_tokens, num_output_tokens = [], [], []
        for span in trace:
            # todo: parse not only match tool
            if "match" in span:
                latencies.append(span["match"]["latency"])
            elif "model" in span:
                num_model_calls.append(span["model"]["num_model_calls"])
                num_input_tokens.append(span["model"]["num_input_tokens"])
                num_output_tokens.append(span["model"]["num_output_tokens"])
        return {
            "latency": latencies,
            "num_model_calls": num_model_calls,
            "num_input_tokens": num_input_tokens,
            "num_output_tokens": num_output_tokens,
            "avg_latency": sum(latencies) / len(latencies) if latencies else None,
            "total_model_calls": sum(num_model_calls),
            "total_input_tokens": sum(num_input_tokens),
            "total_output_tokens": sum(num_output_tokens),
            # todo:
            #  compartmentalize the cost in each model call
            #  since the model can be different across calls
            "cost": openai.get_cost(
                model=libem.parameter.model(),
                num_input_tokens=sum(num_input_tokens),
                num_output_tokens=sum(num_output_tokens),
            ),
        }

"""A global tracer object that libem tools reports to."""
trace = Trace().start()
