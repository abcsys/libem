import libem


def positive():
    e1 = "zero-g zero-g pro pack for garageband ( appleloops ) 169.95"
    e2 = "east west propack for garageband av production software 152.96"

    is_match = libem.match(e1, e2)

    print(f"Entity 1: {e1}\nEntity 2: {e2}\nMatch: {is_match}")


if __name__ == '__main__':
    positive()
