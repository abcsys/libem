import os
import cv2
import libem

from libem.match.prompt import rules
from libem.struct import MultimodalRecord


parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_image(name):
    return cv2.imread(os.path.join(parent_directory, f"test/images/{name}.jpg"))


def positive():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - W/S"

    is_match = libem.match(e1, e2)

    print("Entity 1:", e1)
    print("Entity 2:", e2)
    print("Match:", is_match['answer'])


def negative():
    e1 = "Dyson Hot+Cool AM09 Jet Focus heater and fan, White/Silver"
    e2 = "Dyson AM09 Hot + Cool Jet Focus Fan Heater - Black japan"

    rules.add("Color differentiates entities.")
    is_match = libem.match(e1, e2)

    print()
    print("Entity 1:", e1)
    print("Entity 2:", e2)
    print("Match:", is_match['answer'])


def multimodal():
    e1 = MultimodalRecord(text={"name": "fuji apple", "color": "red"},
                          images=[get_image("apple")])
    e2 = MultimodalRecord(text={"name": "sweet seedless orange", "color": "orange"},
                          images=[get_image("orange1"), get_image("orange2")])

    is_match = libem.match(e1, e2)

    print()
    print("Entity 1:", e1.text, f"with {len(e1.images)} image(s)")
    print("Entity 2:", e2.text, f"with {len(e2.images)} image(s)")
    print("Match:", is_match['answer'])


if __name__ == '__main__':
    positive()
    negative()
    multimodal()
