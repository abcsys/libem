import libem

def main():
    libem.calibrate({
        "libem.match.parameter.likelihood": True
    })

    left, right = "apple inc.", "Apple company"
    is_match = libem.match(left, right)

    print("Entity 1:", left, "\nEntity 2:", right)
    print("Match likelihood:", is_match["likelihood"])


    left, right = "apple inc.", "Applebee's"
    is_match = libem.match(left, right)

    print("Entity 1:", left, "\nEntity 2:", right)
    print("Match likelihood:", is_match["likelihood"])

    left, right = "apple", "Apple electronics"
    is_match = libem.match(left, right)

    print("Entity 1:", left, "\nEntity 2:", right)
    print("Match likelihood:", is_match["likelihood"])


if __name__ == '__main__':
    main()
