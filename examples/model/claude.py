import libem

from libem.match.prompt import rules

def positive():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - W/S"

    is_match = libem.match(e1, e2)

    print("Entity 1:", e1)
    print("Entity 2:", e2)
    print("Match:", is_match['answer'])

def negative():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - Black japan"

    rules.add("Color differentiates entities.")
    is_match = libem.match(e1, e2)

    print("Entity 1:", e1)
    print("Entity 2:", e2)
    print("Match:", is_match['answer'])

def main():
    libem.calibrate({
        "libem.match.parameter.model": "claude-3-5-sonnet-20240620",
    }, verbose=True)
    positive()
    negative()

if __name__ == '__main__':
    main()