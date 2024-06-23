import re
from fuzzywuzzy import fuzz

from libem.block import parameter

schema = {}


def func(left: list[str | dict], right: list[str | dict]) -> list[dict]:
    left_strs, right_strs = [], []
    out = []

    for l in left:
        if type(l) is dict:
            left_str = []
            for v in l.values():
                left_str.append(
                    ' '.join([i
                              for i in re.sub('[^\s\w]+', '', str(v)).split()
                              if len(i) > 2])
                    )
            left_strs.append(' '.join(i for i in left_str))
        else:
            left_strs.append(' '.join(i for i in re.sub('[^\s\w]+', '', l).split()
                                      if len(i) > 2))

    for r in right:
        if type(r) is dict:
            right_str = []
            for v in r.values():
                right_str.append(
                    ' '.join([i
                              for i in re.sub('[^\s\w]+', '', str(v)).split()
                              if len(i) > 2])
                )
            right_strs.append(' '.join(i for i in right_str))
        else:
            right_strs.append(' '.join(i for i in re.sub('[^\s\w]+', '', r).split()
                                       if len(i) > 2))
    
    for i, l in enumerate(left_strs):
        for j, r in enumerate(right_strs):
            if fuzz.token_set_ratio(l, r) >= parameter.similarity():
                out.append({'left': left[i], 'right': right[j]})
    
    return out
