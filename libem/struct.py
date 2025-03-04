from collections.abc import Iterable, Mapping
from typing import TypedDict
from pydantic import BaseModel
from PIL import Image
import numpy as np

# Input types
TextField = str
TextFields = TextField | Mapping[str, TextField]
ImageField = Image.Image | np.ndarray | str
ImageFields = ImageField | Mapping[str, ImageField] | Iterable[ImageField]


class MultimodalRecord(BaseModel):
    text: TextFields | None = None
    images: ImageFields | None = None
    
    class Config:
        arbitrary_types_allowed = True

# If multiple images belong to the same record 
# (in an Iterable or Mapping), use MultimodalRecord
SingleRecord = TextFields | ImageField | MultimodalRecord
Record = SingleRecord | Iterable[SingleRecord]


class Pair(TypedDict):
    left: Record
    right: Record


Left = Record | Pair | Iterable[Pair]
Right = Record | None


# Output types
class Answer(TypedDict):
    answer: str | float
    confidence: float | None
    explanation: str | None


Output = Answer | list[Answer]


def digest(record: SingleRecord) -> str:
    ''' Generate an MD5 hash for a single record. '''
    import hashlib
    import io
    import json

    match record:
        case str():
            data = record.encode()
        case Mapping():
            data = json.dumps(record, sort_keys=True).encode()
        case np.ndarray():
            data = record.tobytes() + str(record.shape).encode()
        case Image.Image():
            buf = io.BytesIO()
            record.save(buf, format='PNG')
            data = buf.getvalue()
        case MultimodalRecord():
            text = json.dumps(record.text, sort_keys=True).encode()
            images = b''.join([
                digest(image) for image in record.images
            ])
            data = text + images
        case _:
            data = str(record).encode()
    return hashlib.md5(data).hexdigest()
