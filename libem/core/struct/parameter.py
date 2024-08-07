import abc
import typing
import copy


class Tunable(abc.ABC):
    @abc.abstractmethod
    def update(self, value):
        pass

    @abc.abstractmethod
    def search(self, train_data, metric):
        pass


class Index:
    def __init__(self, key: str | int):
        self.key = key

    def __eq__(self, other):
        if isinstance(other, Index):
            return self.key == other.key
        else:
            return self.key == other


class Parameter(Tunable):
    def __init__(self,
                 default: Index | typing.Any,
                 options: dict[typing.Any] | list[typing.Any] = None
                 ):
        self.value = self.v = default
        self.default = default
        self.optimal = self.v
        self.options = options or {}
        if isinstance(self.options, list):
            self.options = {i: o for i, o in enumerate(self.options)}
        super().__init__()

    def __call__(self, *args, **kwargs):
        """
        When called, the instance evaluates and returns its current value. If the
        value is a string, it formats the string with supplied args and kwargs. If
        the value is a callable, it calls the function with supplied args and kwargs.
        """
        value = self.value
        if isinstance(value, Index):
            try:
                value = self.options[self.value.key]
            except KeyError:
                raise KeyError(f"Index {self.value.key} "
                               f"not found in options "
                               f"{list(self.options.keys())}.")
        if callable(value):
            return value(*args, **kwargs)
        if isinstance(value, str):
            return value.format(*args, **kwargs)
        else:
            return value

    def __str__(self):
        return str(self.__call__())

    def __eq__(self, other):
        if isinstance(other, Parameter):
            return self.value == other.value
        else:
            return self.value == other

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return self.add(other).copy()

    def add(self, *parameters):
        """parameters.add(param1, param2, ...)"""
        for param in parameters:
            if isinstance(param, Parameter):
                self.value += param.value
            else:
                self.value += param
        return self

    def update(self, value):
        self.value = self.v = value
        return self

    def search(self, train_data, metric):
        raise NotImplementedError

    def export(self, include_all=False):
        if include_all:
            return {
                'default': self.default,
                'value': self.value,
                'options': self.options,
                'optimal': self.optimal
            }
        else:
            return self.value

    def copy(self):
        return copy.deepcopy(self)
