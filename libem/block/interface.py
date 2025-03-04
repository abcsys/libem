from collections.abc import Iterable

from libem.block.function import func
from libem.struct import Record, Pair


Output = Iterable[Pair]


def block(*records: Record, 
          key: str | list | None = None, 
          ignore: str | list | None = None) -> Output:
    '''
    Perform the blocking stage of entity matching given one or more datasets.
    If multiple datasets are passed in, only block across the datasets.
    
    Output format: [{"left": record, "right": record}, ...]
    '''
    
    return func(*records, key=key, ignore=ignore)
