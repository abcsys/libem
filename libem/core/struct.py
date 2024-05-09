import abc
import typing


class Tunable(abc.ABC):
    @abc.abstractmethod
    def update(self, value):
        pass

    @abc.abstractmethod
    def learn(self, train_data, metric):
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
        if isinstance(self.value, str):
            # format the parameter with inputs
            return self.value.format(*args, **kwargs)
        else:
            return self.value

    def update(self, value):
        self.value = self.v = value
        return self

    def learn(self, train_data, metric):
        raise NotImplementedError

    def search(self, train_data, metric):
        raise NotImplementedError

    def export(self, full=False):
        if full:
            return {
                'default': self.default,
                'value': self.value,
                'options': self.options,
                'optimal': self.optimal
            }
        else:
            return self.value


class Prompt(Parameter):
    @classmethod
    def join(cls, *prompts, sep="\n"):
        return sep.join([*prompts])

    def __init__(self, default: str, options: list[str] = None):
        super().__init__(default, options)
