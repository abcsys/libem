import libem

from libem.core.struct.parameter import Index


def main():
    libem.calibrate({
        "libem.match.prompt.output": Index("likelihood")
    })

    left, right = "apple inc.", "Apple company"
    is_match = libem.match(left, right)

    print("Entity 1:", left, "\nEntity 2:", right)
    print("Match likelihood:", is_match["answer"])


if __name__ == '__main__':
    main()
