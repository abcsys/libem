import os
import cv2
from PIL import Image
import libem

current_directory = os.path.dirname(os.path.abspath(__file__))

def get_image(name):
    return cv2.imread(os.path.join(current_directory, f"images/{name}.jpg"))

def get_pil_image(name):
    return Image.open(os.path.join(current_directory, f"images/{name}.jpg"))

def main():
    # text only
    output = libem.match("apple", "orange")['answer']
    assert output == "no", output
    
    output = libem.match("sweet seedless orange", "orange seedless")['answer']
    assert output == "yes", output
    
    fruits = [
        {"text_fields": {"name": "apple", "color": "red"},
         "image_fields": get_image("apple")},
        {"text_fields": {"name": "sweet seedless orange", "color": "orange"},
         "image_fields": [get_image("orange1"), get_pil_image("orange2")]},
        {"text_fields": {"name": "lemon", "color": "yellow"},
         "image_fields": [get_image("lemon")]},
        {"text_fields": {"name": "fuji apple"}}
    ]
    
    # dict only
    output = libem.match(fruits[0]['text_fields'], fruits[1]['text_fields'])['answer']
    assert output == "no", output
    
    output = libem.match(fruits[1]['text_fields'], fruits[1]['text_fields'])['answer']
    assert output == "yes", output
    
    # dict and image
    output = libem.match(fruits[0], fruits[1])['answer']
    assert output == "no", output
    
    output = libem.match(fruits[1], fruits[2])['answer']
    assert output == "no", output
    
    output = libem.match(fruits[0], fruits[3])['answer']
    assert output == "yes", output
    
    # list input
    output = [o['answer'] for o in libem.match([fruits[0]] * 2, fruits[2:4])]
    assert output == ["no", "yes"], output
    
    # prompt-level batching
    libem.calibrate({
        "libem.match.parameter.batch_size": 5,
    })
    output = [o['answer'] for o in libem.match([fruits[0]] * 2, fruits[2:4])]
    assert output == ["no", "yes"], output
    
    # record-level batching
    libem.calibrate({
        "libem.match.parameter.record_batch": True,
    })
    output = [o['answer'] for o in libem.match([fruits[0]] * 3, fruits[1:])]
    assert output == ["no", "no", "yes"], output
    
    # image only
    fruits = [
        {"image_fields": get_pil_image("apple")},
        {"image_fields": [get_image("orange1"), get_pil_image("orange2")]},
        {"image_fields": [get_image("lemon")]},
        {"text_fields": {"name": "red apple"}}
    ]
    output = [o['answer'] for o in libem.match([fruits[0]] * 3, fruits[1:])]
    assert output == ["no", "no", "yes"], output
    
    print("All tests passed.")

if __name__ == "__main__":
    main()
