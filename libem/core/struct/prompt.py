import copy

from libem.core.struct.parameter import Parameter


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
                case Rules():
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


class Shots(Parameter):
    def __init__(self, default: list[Shot] = None,
                 options: list[list[Shot]] = None):
        super().__init__(default, options)

    def __call__(self):
        _shots = []
        for shot in self.value:
            _shots.extend(shot())
        return _shots

    def __str__(self):
        return str(self.__call__())

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.value)

    def __add__(self, other):
        return self.add(other).copy()

    def __iter__(self):
        return iter(self.value)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Shots(self.value[index])
        elif isinstance(index, int):
            return self.value[index]
        else:
            raise TypeError(f"Invalid argument type: {type(index)}")

    def export(self, include_all=False):
        if include_all:
            return {
                'default': self.default,
                'value': self.value,
                'options': self.options,
                'optimal': self.optimal
            }
        else:
            return f"{len(self.value)} shots"

    def add(self, *shots):
        """shots.add(shot1, shot2, ...)"""
        for shot in shots:
            match shot:
                case Shot():
                    self.value.append(shot)
                case list():
                    self.value.extend(shot)
                case Shots():
                    self.value.extend(shot.shots)
                case _:
                    raise ValueError(f"Invalid shot type "
                                     f"{type(shot)} for {shot}")
        return self

    def copy(self):
        return copy.deepcopy(self)


class Prompt(Parameter):
    @classmethod
    def join(cls, *prompts, sep="\n"):
        to_join = []
        for prompt in prompts:
            _prompt = ""
            match prompt:
                case str():
                    _prompt = prompt
                case Rules():
                    _prompt = prompt()
                case Experiences():
                    _prompt = prompt()
                case _:
                    raise ValueError(f"Invalid prompt type to join:"
                                     f"{type(prompt)} for {prompt}")
            if len(_prompt.strip()) > 0:
                to_join.append(_prompt)
        return sep.join(to_join)

    def __init__(self, default: str | Shots | Rules | Experiences,
                 options: list[str | Shots | Rules | Experiences] = None):
        super().__init__(default, options)
