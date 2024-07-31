import time
import numpy as np
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

    def reset(self):
        self.readings = []
        return self

    def readings(self):
        return self.readings

    def sum(self):
        if len(self.readings) == 0:
            return None
        return sum(self.readings)

    def mean(self):
        if len(self.readings) == 0:
            return None
        return np.mean(self.readings)

    def std(self):
        if len(self.readings) == 0:
            return None
        return np.std(self.readings)

    def min(self):
        return min(self.readings, default=None)

    def max(self):
        return max(self.readings, default=None)

    def report(self):
        return {
            "sum": self.sum(),
            "mean": self.mean(),
            "std": self.std(),
            "min": self.min(),
            "max": self.max(),
        }


TelemetrySpec = str | list[str] | Telemetry | list[Telemetry]


class Trace:
    """Collects a trace of structured outputs"""

    def __init__(self, telemetry: TelemetrySpec = None):
        self.trace = []
        self.history = []

        self._telemetry = []
        self.add_telemetry(telemetry)

        self._trace_start = 0
        self._trace_duration = 0

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
        _trace = self.trace.copy()
        if _trace:
            self.history.append(_trace)
        self.trace = []

        for telemetry in self._telemetry:
            telemetry.reset()

        self._trace_duration = 0
        self._trace_start = time.time()
        return self

    def stop(self):
        """Stops tracing."""
        self._trace_duration = time.time() - self._trace_start
        return self

    def add(self, span):
        """Starts tracing."""
        self.trace.append(span)
        return self

    def get(self, include_history=False):
        if include_history:
            return list(
                chain.from_iterable(
                    self.history + [self.trace]
                )
            )
        else:
            return self.trace

    def telemetry(self, *args, **kwargs):
        return self.stats(*args, **kwargs)

    def stats(self,
              flatten=False,
              include_history=False,
              include_readings=False):
        _trace = self.get(include_history=include_history)

        stats = {}
        for span in _trace:
            for telemetry in self._telemetry:
                telemetry.add(span)

        for telemetry in self._telemetry:
            stats[telemetry.name] = telemetry.report()
            if include_readings:
                stats[telemetry.name]["readings"] = telemetry.readings

        if flatten:
            return stats
        else:
            return nest(stats)

    def duration(self):
        return self._trace_duration

    def add_telemetry(self, telemetry: TelemetrySpec):
        match telemetry:
            case str():
                self._telemetry.append(Telemetry(telemetry))
            case Telemetry():
                self._telemetry.append(telemetry)
            case list():
                for t in telemetry:
                    if isinstance(t, str):
                        self._telemetry.append(Telemetry(t))
                    elif isinstance(t, Telemetry):
                        self._telemetry.append(t)
                    else:
                        raise ValueError(f"Unknown telemetry type: {type(t)}; "
                                         f"must be one of {TelemetrySpec}")
        return self


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
