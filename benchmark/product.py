import libem
from libem.prepare.datasets import amazon_google


def main():
    num_pair = 5
    print(f"Matching {num_pair} from Amazon Google product dataset.")
    for i, data in enumerate(amazon_google.read_test()):
        print("\nPair: ", i)
        e1 = data['left']
        e2 = data['right']
        label = data['label']

        is_match = libem.match(e1, e2)

        print(f"Entity 1: {e1}\nEntity 2: {e2}\nMatch: {is_match}; label: {label}\n")
        if i >= num_pair:
            break
    print("Done.")


if __name__ == "__main__":
    main()
