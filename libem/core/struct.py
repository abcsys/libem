import typing


class Parameter:
    def __init__(self, default: typing.Any, options: list[typing.Any] = None):
        self.value = self.v = default
        self.default = default
        self.options = options or []

    def __call__(self, *args, **kwargs):
        if isinstance(self.value, str):
            return self.value.format(*args, **kwargs)
        return self.value


class Prompt:
    @classmethod
    def join(cls, *prompts, sep=" "):
        return sep.join([*prompts])

    def __init__(self, default: str, options: list[str] = None):
        self.value = self.v = default
        self.default = default
        self.options = options or []

    def __call__(self, *args, **kwargs):
        """Format the prompt with the given arguments."""
        return self.value.format(*args, **kwargs)
