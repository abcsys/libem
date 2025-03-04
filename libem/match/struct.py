from collections.abc import (
    Iterable, Generator, Iterator
)
from libem.struct import *
from libem.match import parameter


# internal types
class _MultimodalRecord(BaseModel):
    text: str | None = None
    images: list[str | np.ndarray] | None = None
    
    class Config:
        arbitrary_types_allowed = True

_Left = _MultimodalRecord | list[_MultimodalRecord]
_Right = _MultimodalRecord | list[_MultimodalRecord]


def parse_input(left: Left, right: Right) -> tuple[_Left, _Right]:
    if right is None:
        # when pairs are given in a single parameter,
        # parse the pair into left and right
        pair = left
        match pair:
            case Mapping():
                try:
                    left, right = pair["left"], pair["right"]
                except KeyError:
                    raise ValueError(
                        f"unexpected input type: {type(pair)}," 
                        f"must be {Pair}."
                    )
            case Iterable():
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
    
    left, right = encode_entity_fields(left), encode_entity_fields(right)
    if isinstance(left, list):
        assert len(left) == len(right)
    
    return left, right


def encode_entity_fields(entity_fields: Record) -> _MultimodalRecord | list[_MultimodalRecord]:
    match entity_fields:
        case str() | Mapping():
            return _MultimodalRecord(text=encode_text_fields(entity_fields))
        case Image.Image() | np.ndarray():
            return _MultimodalRecord(images=encode_image_fields(entity_fields))
        case MultimodalRecord():
            _entity_fields = _MultimodalRecord()
            if entity_fields.text is not None:
                _entity_fields.text = encode_text_fields(entity_fields.text)
            if entity_fields.images is not None:
                _entity_fields.images = encode_image_fields(entity_fields.images)
            return _entity_fields
        case Iterable():
            return [encode_entity_fields(e) for e in entity_fields]
        case _:
            raise ValueError(
                f"unexpected input type: {type(entity_fields)},"
                f"must be {Left}."
            )


def encode_text_fields(text_fields: TextFields) -> str:
    if isinstance(text_fields, Mapping):
        return parameter.dict_desc_encoding(text_fields)
    return text_fields


def encode_image_fields(images: ImageFields) -> list[np.ndarray]:
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
        case Mapping():
            return [convert_pil(value) for value in images.values()]
        case Iterable():
            return [convert_pil(value) for value in images]
        case _:
            raise ValueError(
                f"unexpected input type: {type(images)},"
                f"must be {ImageFields}."
            )
