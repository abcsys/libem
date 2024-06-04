from libem.core.struct import Prompt

description = Prompt(
    default="Searches the internet. Returns a snippet "
            "of the top 3 results if available.",
    options=[]
)
rule = Prompt(
    default=Prompt.Rule(["Use when you are unsure about your decision. "
                         "You may invoke the tool multiple times."]),
    options=[]
)
