from libem.core.struct import Prompt

description = Prompt(
    default="Browse the web to find descriptions for "
            "the given entity."
)
rule = Prompt(
    default=Prompt.Rule(["Use only when you think it would help "
                         "with the matching task. "])
)
