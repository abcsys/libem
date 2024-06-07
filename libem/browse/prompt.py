from libem.core.struct import Prompt

description = Prompt(
    default="Browse the web to find relevant information about the entities."
)
rule = Prompt(
    default=Prompt.Rule([
        "Do not use this tool if you can already decide "
        "with the entity descriptions.",
    ])
)
