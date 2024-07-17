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


class Parameter(Tunable):
    def __init__(self,
                 default: typing.Any,
                 options: list[typing.Any] = None
                 ):
        self.value = self.v = default
        self.default = default
        self.options = options or []
        self.optimal = self.v
        super().__init__()

    def __call__(self, *args, **kwargs):
        """
        When called, the instance evaluates and returns its current value. If the
        value is a string, it formats the string with supplied args and kwargs. If
        the value is callable, it calls the function with supplied args and kwargs.
        If the value contains other `Parameter` instances or similarly
        dynamically-resolvable structures, it will recursively resolve these
        before returning.
        """
        if isinstance(self.value, str):
            return self.value.format(*args, **kwargs)
        if callable(self.value):
            return self.value(*args, **kwargs)
        else:
            return self.value

    def __str__(self):
        return str(self.__call__())

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
