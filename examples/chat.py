import libem


def positive():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - W/S - japan"

    is_match: str = libem.chat(f"Match two entities "
                               f"entity 1: {e1}; "
                               f"entity 2: {e2}")

    print("Entity 1:", e1)
    print("Entity 2:", e2)
    print("Match:", is_match)


if __name__ == '__main__':
    positive()
