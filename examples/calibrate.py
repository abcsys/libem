import libem

from libem.core.struct import Prompt


def main():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - Black japan"

    print("Calibrate the match to use no tool")
    libem.calibrate({
        "libem.match.parameter.tools": [],  # turn off sub-tools
    }, verbose=True)

    print("Calibrate the match to ignore colors")
    libem.calibrate({
        "libem.match.prompt.rule": Prompt.Rules(["Ignore colors."]),
    }, verbose=True)

    is_match = libem.match(e1, e2)
    
    print("Entity 1:", e1)
    print("Entity 2:", e2)
    print("Match:", is_match['answer'])

    print("")
    print("Calibrate the match to consider colors")
    libem.calibrate({
        "libem.match.prompt.rule": Prompt.Rules(["Color distinguishes entities."]),
    }, verbose=True)

    is_match = libem.match(e1, e2)

    print("Entity 1:", e1)
    print("Entity 2:", e2)
    print("Match:", is_match['answer'])

    print("")
    print("Calibrate the match to use browse tool")
    libem.calibrate({
        "libem.match.parameter.tools": ["libem.browse"],
    }, verbose=True)

    is_match = libem.match(e1, e2)

    print("Entity 1:", e1)
    print("Entity 2:", e2)
    print("Match:", is_match['answer'])


if __name__ == "__main__":
    main()
