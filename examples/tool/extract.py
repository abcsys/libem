import libem

import pprint as pp


def main():
    desc = "Elon Musk, the CEO of Tesla and SpaceX, " \
           "spoke at a major tech conference in San Francisco " \
           "on January 5th, 2023."
    entities = libem.extract(desc)

    pp.pprint(entities)

if __name__ == '__main__':
    main()
