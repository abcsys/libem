import libem
from libem.match.prompt import rules


def test_positive():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - W/S"

    is_match = libem.match(e1, e2)

    assert is_match['answer'] == 'yes', f"Expected match to be 'yes', but got {is_match['answer']}"


def test_negative():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - Black japan"

    rules.add("Color differentiates entities.")
    is_match = libem.match(e1, e2)

    assert is_match['answer'] == 'no', f"Expected match to be 'no', but got {is_match['answer']}"
