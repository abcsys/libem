import libem
import pprint

pp = pprint.PrettyPrinter(sort_dicts=False)


def main():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - Black japan"

    print("Trace 1:")
    with libem.trace as t:
        _ = libem.match(e1, e2)
        pp.pprint(t.get())

    e1 = "Supplier X, Item: Widget, Qty: 100, Price: $5"
    e2 = "X Supplier, Widget, Quantity: 100, Unit Price: $5"

    print("Trace 2:")
    with libem.trace as t:
        _ = libem.match(e1, e2)
        pp.pprint(t.get())


if __name__ == '__main__':
    main()
