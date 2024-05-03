import libem


def main():
    e1 = "Supplier X, Item: Widget, Qty: 100, Price: $5"
    e2 = "X Supplier, Widget, Quantity: 100, Unit Price: $5"
    is_match = libem.match(e1, e2)

    print(f"entity 1: {e1} \nentity 2: {e2} \nMatch: {is_match}")


if __name__ == '__main__':
    main()
