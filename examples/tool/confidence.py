import libem


def main():
    libem.calibrate({"libem.match.parameter.confidence": True})

    left, right = "apple inc.", "Apple company"
    is_match = libem.match(left, right)

    print("Entity 1:", left, "\nEntity 2:", right)
    print("Match:", is_match["answer"])
    print("Confidence:", is_match["confidence"])


if __name__ == '__main__':
    main()
