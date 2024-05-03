import libem


def positive():
    e1 = "Supplier X, Item: Widget, Qty: 100, Price: $5"
    e2 = "X Supplier, Widget, Quantity: 100, Unit Price: $5"

    is_match = libem.match(e1, e2)

    print(f"Entity 1: {e1}\nEntity 2: {e2}\nMatch: {is_match}")


if __name__ == '__main__':
    positive()
