import libem


def positive():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - W/S"

    is_match = libem.match(e1, e2)

    print(f"Entity 1: {e1}\nEntity 2: {e2}\nMatch: {is_match}")


if __name__ == '__main__':
    positive()
