import libem

from libem.core.struct import Prompt

def main():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - Black japan"

    print("Calibrate the match to use no tool")
    libem.calibrate({
        "libem.match.parameter.tools": [],  # turn off sub-tools
    }, verbose=True)
    is_match = libem.match(e1, e2)
    print(f"Entity 1: {e1}\nEntity 2: {e2}\n"
          f"Match: {is_match}")

    print("")
    print("Calibrate the match to ignore colors")
    libem.calibrate({
        "libem.match.prompt.rule": Prompt.Rule(["Ignore colors."]),
    }, verbose=True)
    is_match = libem.match(e1, e2)
    print(f"Entity 1: {e1}\nEntity 2: {e2}\n"
          f"Match: {is_match}")

    print("")
    print("Calibrate the match to use browse tool")
    libem.calibrate({
        "libem.match.parameter.tools": ["libem.browse"],
    }, verbose=True)
    is_match = libem.match(e1, e2)
    print(f"Entity 1: {e1}\nEntity 2: {e2}\n"
          f"Match: {is_match}")

    print("")
    print("Calibrate the match to consider colors")
    libem.calibrate({
        "libem.match.prompt.rule": Prompt.Rule(["Color distinguishes entities."]),
    }, verbose=True)
    is_match = libem.match(e1, e2)
    print(f"Entity 1: {e1}\nEntity 2: {e2}\n"
          f"Match: {is_match}")

if __name__ == "__main__":
    main()