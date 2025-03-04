from libem.struct import *


# internal types
class _TextRecord(BaseModel):
    text: str | Mapping

class _ImageRecord(BaseModel):
    image: ImageField
    class Config:
        arbitrary_types_allowed = True

_Record = _TextRecord | _ImageRecord | MultimodalRecord


def parse_input(record: Record) -> list[_Record]:
    match record:
        case str() | Mapping():
            return [_TextRecord(text=record)]
        case Image.Image() | np.ndarray():
            return [_ImageRecord(image=record)]
        case MultimodalRecord():
            return [record]
        case Iterable():
            output = []
            for r in record:
                output.extend(parse_input(r))
            return output
        case _:
            raise ValueError(
                f"unexpected input type: {type(record)},"
                f"must be {Record}."
            )
