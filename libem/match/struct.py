from libem.match import parameter
from typing import TypedDict
from pydantic import BaseModel
from collections.abc import (
    Iterable, Generator, Iterator
)
from PIL import Image
import numpy as np

# input types
TextEntityField = str
TextEntityFields = TextEntityField | dict[str, TextEntityField]
ImageEntityField = Image.Image | np.ndarray | str
ImageEntityFields = ImageEntityField | dict[str, ImageEntityField]


class MultimodalEntityDesc(BaseModel):
    text: TextEntityFields | None = None
    images: ImageEntityFields | list[ImageEntityField] | None = None
    
    class Config:
        arbitrary_types_allowed = True


EntityDesc = TextEntityFields | list[TextEntityFields] | \
             ImageEntityFields | list[ImageEntityFields] | \
             MultimodalEntityDesc | list[MultimodalEntityDesc]


class Pair(TypedDict):
    left: EntityDesc
    right: EntityDesc


Left = EntityDesc | Pair | list[Pair]
Right = EntityDesc | None


# output types
class Answer(TypedDict):
    answer: str | float
    confidence: float | None
    explanation: str | None


Output = Answer | list[Answer]


# internal types
class _MultimodalEntityDesc(BaseModel):
    text: str | None = None
    images: list[str | np.ndarray] | None = None
    
    class Config:
        arbitrary_types_allowed = True

_Left = _MultimodalEntityDesc | list[_MultimodalEntityDesc]
_Right = _MultimodalEntityDesc | list[_MultimodalEntityDesc]


def parse_input(left: Left, right: Right) -> tuple[_Left, _Right]:
    if right is None:
        # when pairs are given in a single parameter,
        # parse the pair into left and right
        pair = left
        match pair:
            case dict():
                try:
                    left, right = pair["left"], pair["right"]
                except KeyError:
                    raise ValueError(
                        f"unexpected input type: {type(pair)}," 
                        f"must be {Pair}."
                    )
            case _ if isinstance(pair, Iterable):
                if isinstance(pair, Generator) or isinstance(pair, Iterator):
                    pair = list(pair)
                try:
                    left = [p["left"] for p in pair]
                    right = [p["right"] for p in pair]
                except KeyError:
                    raise ValueError(
                        f"unexpected input type: {type(pair)},"
                        f"must be {Pair}."
                    )
            case _:
                raise ValueError(
                    f"unexpected input type: {type(pair)},"
                    f"must be {Pair}."
                )

    assert type(left) == type(right)
    if isinstance(left, list):
        assert len(left) == len(right)
    
    return encode_entity_fields(left), encode_entity_fields(right)


def encode_entity_fields(entity_fields: EntityDesc) -> _MultimodalEntityDesc | list[_MultimodalEntityDesc]:
    match entity_fields:
        case str() | dict():
            return _MultimodalEntityDesc(text=encode_text_fields(entity_fields))
        case Image.Image() | np.ndarray():
            return _MultimodalEntityDesc(images=encode_image_fields(entity_fields))
        case MultimodalEntityDesc():
            _entity_fields = _MultimodalEntityDesc()
            if entity_fields.text is not None:
                _entity_fields.text = encode_text_fields(entity_fields.text)
            if entity_fields.images is not None:
                _entity_fields.images = encode_image_fields(entity_fields.images)
            return _entity_fields
        case list():
            return [encode_entity_fields(e) for e in entity_fields]
        case _:
            raise ValueError(
                f"unexpected input type: {type(entity_fields)},"
                f"must be {Left}."
            )


def encode_text_fields(text_fields: TextEntityFields) -> str:
    if isinstance(text_fields, dict):
        return parameter.dict_desc_encoding(text_fields)
    return text_fields


def encode_image_fields(images: ImageEntityFields) -> list[np.ndarray]:
    
    def convert_pil(img):
        """
        Convert a PIL Image to an OpenCV image (NumPy array).
        """
        import cv2
        
        match img:
            case str() | np.ndarray():
                return img
            case Image.Image():
                cv_img = np.array(img)
                
                if img.mode == "RGB":
                    return cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
                elif img.mode == "RGBA":
                    return cv2.cvtColor(cv_img, cv2.COLOR_RGBA2BGRA)
            case _:
                raise ValueError(
                    f"unexpected input type: {type(img)},"
                    f"must be {Image.Image}."
                )
    
    match images:
        case str() | Image.Image() | np.ndarray():
            return [convert_pil(images)]
        case dict():
            return [convert_pil(value) for value in images.values()]
        case list():
            return [convert_pil(value) for value in images]
        case _:
            raise ValueError(
                f"unexpected input type: {type(images)},"
                f"must be {ImageEntityFields}."
            )
