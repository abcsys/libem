import numpy as np
from typing import Union, List
from itertools import chain


class Telemetry:
    metrics = {"sum", "mean", "std", "min", "max"}

    def __init__(self, name, metrics: list | set = None):
        self.name = name
        self.readings = []

        if metrics is None:
            self.metrics = Telemetry.metrics
        else:
            for metric in metrics:
                if metric not in Telemetry.metrics:
                    raise ValueError(f"Unknown metric: {metric};"
                                     f" must be one of {Telemetry.metrics}")
            self.metrics = metrics

    def add(self, record: dict | int | float):
        if isinstance(record, dict):
            # traverse the record to get the reading value
            reading = record.copy()
            path = self.name.split(".")
            for key in path:
                reading = reading.get(key, {})

            if not reading:
                return self
        else:
            reading = record

        self.readings.append(reading)
        return self

    def readings(self):
        return self.readings

    def sum(self):
        return sum(self.readings)

    def mean(self):
        return np.mean(self.readings)

    def std(self):
        return np.std(self.readings)

    def min(self):
        return min(self.readings)

    def max(self):
        return max(self.readings)

    def report(self):
        return {
            "sum": self.sum(),
            "mean": self.mean(),
            "std": self.std(),
            "min": self.min(),
            "max": self.max(),
        }


TelemetrySpec = Union[str, 'Telemetry', List[str], List['Telemetry']]


class Trace:
    """Collects a trace of structured outputs"""

    def __init__(self, telemetry: TelemetrySpec = None):
        self.trace = []
        self.history = []

        self.telemetry = []
        self.add_telemetry(telemetry)

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
        trace = self.trace.copy()
        if trace:
            self.history.append(trace)
        self.trace = []
        return self

    def stop(self):
        """Stops tracing."""
        return self

    def add(self, span):
        """Starts tracing."""
        self.trace.append(span)
        return self

    def get(self, all=False):
        if all:
            return list(
                chain.from_iterable(
                    self.history + [self.trace]
                )
            )
        else:
            return self.trace

    def add_telemetry(self, telemetry: TelemetrySpec):
        match telemetry:
            case str():
                self.telemetry.append(Telemetry(telemetry))
            case Telemetry():
                self.telemetry.append(telemetry)
            case list():
                for t in telemetry:
                    if isinstance(t, str):
                        self.telemetry.append(Telemetry(t))
                    elif isinstance(t, Telemetry):
                        self.telemetry.append(t)
                    else:
                        raise ValueError(f"Unknown telemetry type: {type(t)}; "
                                         f"must be one of {TelemetrySpec}")
        return self

    def stats(self, all=False, flatten=False, readings=False):
        trace = self.get(all=all)

        stats = {}
        for span in trace:
            for telemetry in self.telemetry:
                telemetry.add(span)

        for telemetry in self.telemetry:
            stats[telemetry.name] = telemetry.report()
            if readings:
                stats[telemetry.name]["readings"] = telemetry.readings

        if flatten:
            return stats
        else:
            return nest(stats)


def nest(flat_dict):
    nested = {}
    for flat_key, values in flat_dict.items():
        parts = flat_key.split('.')
        current_level = nested
        for part in parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        current_level[parts[-1]] = values
    return nested


"""A global tracer object that libem tools reports to."""
trace = Trace(
    telemetry=[
        Telemetry("match.latency"),
        Telemetry("model.num_model_calls"),
        Telemetry("model.num_input_tokens"),
        Telemetry("model.num_output_tokens"),
    ],
).start()
