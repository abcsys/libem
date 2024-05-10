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

    def __str__(self):
        return str(self.__call__())

    def __repr__(self):
        return self.__str__()

    def update(self, value):
        self.value = self.v = value
        return self

    def learn(self, train_data, metric):
        raise NotImplementedError

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


class Prompt(Parameter):
    class Rule:
        def __init__(self, rules: list[str] = None,
                     intro: str = "Rules to follow:",
                     sep="\n", bullet="-"):
            self.rules = rules or []
            self.intro = intro
            self.sep = sep
            self.bullet = bullet

        def __call__(self, *args, **kwargs):
            if len(self.rules) == 0:
                return ""
            rules = [f"{self.bullet} {rule}" for rule in self.rules
                     if len(rule.strip()) != ""]
            return f"{self.intro}\n" \
                   f"{self.sep.join(rules)}"

        def __str__(self):
            return str(self.__call__())

        def __repr__(self):
            return self.__str__()

        def __len__(self):
            return len(self.rules)

        def __add__(self, other):
            assert isinstance(other, self.__class__)
            return Prompt.Rule(self.rules + other.rules)

        def add(self, *rules):
            """rule.add(rule1, rule2, rule3)"""
            for rule in rules:
                self.rules.extend(rule.rules)
            return self

        def export(self, *args, **kwargs):
            _, _ = args, kwargs
            return self.__call__()

    class Experience:
        def __init__(self, mistakes: list[str] = None,
                     intro: str = "Mistakes to avoid:",
                     sep="\n", bullet="-"):
            self.mistakes = mistakes or []
            self.intro = intro
            self.sep = sep
            self.bullet = bullet

        def __call__(self, *args, **kwargs):
            if len(self.mistakes) == 0:
                return ""
            mistakes = [f"{self.bullet} {mistake}" for mistake in self.mistakes
                        if len(mistake.strip()) != ""]
            return f"{self.intro}\n" \
                   f"{self.sep.join(mistakes)}"

        def __str__(self):
            return str(self.__call__())

        def __repr__(self):
            return self.__str__()

        def __len__(self):
            return len(self.mistakes)

        def __add__(self, other):
            assert isinstance(other, self.__class__)
            return Prompt.Experience(self.mistakes + other.mistakes)

        def add(self, *mistakes):
            """mistake.add(mistake1, mistake2, mistake3)"""
            for mistake in mistakes:
                self.mistakes.extend(mistake.miscakes)
            return self

        def export(self, *args, **kwargs):
            _, _ = args, kwargs
            return self.__call__()

    @classmethod
    def join(cls, *prompts, sep="\n"):
        to_join = []
        for prompt in prompts:
            if isinstance(prompt, str):
                to_join.append(prompt)
            elif isinstance(prompt, (cls.Rule, cls.Experience)):
                to_join.append(prompt())
        return sep.join(to_join)

    def add(self, *prompts, sep="\n"):
        self.update(Prompt.join(self.value, *prompts, sep=sep))
        return self

    def prepend(self, *prompts, sep="\n"):
        self.update(Prompt.join(*prompts, self.value, sep=sep))
        return self

    def __init__(self, default: str | Rule | Experience,
                 options: list[str | Rule | Experience] = None):
        super().__init__(default, options)


CoT = chain_of_thought = Prompt(
    default="Explain your answer step by step.",
    options=[""],
)

# todo
ReAct = reason_act = Prompt(
    default="",
    options=[""],
)
