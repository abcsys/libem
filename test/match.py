import os
import cv2
from PIL import Image
import libem
from libem.struct import MultimodalRecord

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
        MultimodalRecord(text={"name": "apple", "color": "red"}, 
                         images=get_image("apple")),
        MultimodalRecord(text={"name": "sweet seedless orange", "color": "orange"}, 
                         images=[get_image("orange1"), get_image("orange2")]),
        MultimodalRecord(text={"name": "lemon", "color": "yellow"}, 
                         images=[get_image("lemon")]),
        MultimodalRecord(text={"name": "fuji apple"})
    ]
    
    # dict only
    output = libem.match(fruits[0].text, fruits[1].text)['answer']
    assert output == "no", output
    
    output = libem.match(fruits[1].text, fruits[1].text)['answer']
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
        MultimodalRecord(images=get_pil_image("apple")),
        MultimodalRecord(images=[get_image("orange1"), get_pil_image("orange2")]),
        MultimodalRecord(text={"name": "red apple"}),
        MultimodalRecord(images=["https://media.istockphoto.com/id/184276818/photo/red-apple.jpg?s=612x612&w=0&k=20&c=NvO-bLsG0DJ_7Ii8SSVoKLurzjmV0Qi4eGfn6nW3l5w="])
    ]
    output = [o['answer'] for o in libem.match([fruits[0]] * 3, fruits[1:])]
    assert output == ["no", "yes", "yes"], output
    
    print("All tests passed.")

if __name__ == "__main__":
    main()
