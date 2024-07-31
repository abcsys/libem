from libem.core.struct import Parameter
from libem.interface import block, match

block_func = Parameter(
    default=block,
)

match_func = Parameter(
    default=match,
)
