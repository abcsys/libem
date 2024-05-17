import abc
import typing
import copy


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

    def copy(self):
        return copy.deepcopy(self)


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
            match other:
                case str():
                    return Prompt.Rule(self.rules + [other])
                case list():
                    return Prompt.Rule(self.rules + other)
                case Prompt.Rule():
                    return Prompt.Rule(self.rules + other.rules)
                case _:
                    raise ValueError(f"Invalid rule type "
                                     f"{type(other)} for {other}")

        def add(self, *rules):
            """rule.add(rule1, rule2, ...)"""
            for rule in rules:
                match rule:
                    case str():
                        self.rules.append(rule)
                    case list():
                        self.rules.extend(rule)
                    case _:
                        raise ValueError(f"Invalid rule type "
                                         f"{type(rule)} for {rule}")
            return self

        def export(self, *args, **kwargs):
            _, _ = args, kwargs
            return self.__call__()

        def copy(self):
            return copy.deepcopy(self)

    class Experience(Rule):
        def __init__(self, mistakes: list[str] = None,
                     intro: str = "Mistakes to avoid:",
                     sep="\n", bullet="*"):
            super().__init__(rules=mistakes,
                             intro=intro,
                             sep=sep,
                             bullet=bullet)

    @classmethod
    def join(cls, *prompts, sep="\n"):
        to_join = []
        for prompt in prompts:
            match prompt:
                case str():
                    to_join.append(prompt)
                case cls.Rule():
                    to_join.append(prompt())
                case cls.Experience():
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
