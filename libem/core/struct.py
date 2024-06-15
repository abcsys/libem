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


class Shot:
    def __init__(self, question: str = None,
                 answer: str = None,
                 question_role="user",
                 answer_role="assistant"):
        self.question = question
        self.answer = answer
        self.question_role = question_role
        self.answer_role = answer_role

    def __call__(self):
        if self.question is None or self.answer is None:
            return []
        else:
            return [
                {"role": self.question_role, "content": self.question},
                {"role": self.answer_role, "content": self.answer},
            ]

    def __str__(self):
        return str(self.__call__())

    def __repr__(self):
        return self.__str__()


class Prompt(Parameter):
    class Shots:
        def __init__(self, shots: list[Shot] = None):
            self.shots = shots or []

        def __call__(self):
            _shots = []
            for shot in self.shots:
                _shots.extend(shot())
            return _shots

        def __str__(self):
            return str(self.__call__())

        def __repr__(self):
            return self.__str__()

        def __len__(self):
            return len(self.shots)

        def __add__(self, other):
            return self.add(other).copy()

        def add(self, *shots):
            """shots.add(shot1, shot2, ...)"""
            for shot in shots:
                match shot:
                    case Shot():
                        self.shots.append(shot)
                    case list():
                        self.shots.extend(shot)
                    case Prompt.Shots():
                        self.shots.extend(shot.shots)
                    case _:
                        raise ValueError(f"Invalid shot type "
                                         f"{type(shot)} for {shot}")
            return self

        def export(self):
            return self.__call__()

        def copy(self):
            return copy.deepcopy(self)

    class Rules:
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
            return self.add(other).copy()

        def add(self, *rules):
            """rule.add(rule1, rule2, ...)"""
            for rule in rules:
                match rule:
                    case str():
                        self.rules.append(rule)
                    case list():
                        self.rules.extend(rule)
                    case Prompt.Rules():
                        self.rules.extend(rule.rules)
                    case _:
                        raise ValueError(f"Invalid rule type to add:"
                                         f"{type(rule)} for {rule}")
            return self

        def export(self):
            return self.__call__()

        def copy(self):
            return copy.deepcopy(self)

    class Experiences(Rules):
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
            _prompt = ""
            match prompt:
                case str():
                    _prompt = prompt
                case cls.Rules():
                    _prompt = prompt()
                case cls.Experiences():
                    _prompt = prompt()
                case cls.Shots():
                    _prompt = str(prompt())
                case _:
                    raise ValueError(f"Invalid prompt type to join:"
                                     f"{type(prompt)} for {prompt}")
            if len(_prompt.strip()) > 0:
                to_join.append(_prompt)
        return sep.join(to_join)

    def __init__(self, default: str | Shots | Rules | Experiences,
                 options: list[str | Shots | Rules | Experiences] = None):
        super().__init__(default, options)


CoT = chain_of_thought = Prompt(
    default='Explain your answer step by step.',
)

Confidence = Prompt(
    default="Give a confidence score from 1 to 5, with 1 being a guess "
            "and 5 being fully confident, give the score only, do not justify.",
)
