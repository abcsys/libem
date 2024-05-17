from libem.core.struct import Prompt
from libem.match.prompt import rule

recap_results = Prompt(
    default=f"Current ruleset:\n{rule}\n\n"
            "Here is a sample of the predictions you made "
            "following the ruleset on entity matching:\n"
            "{results}\n\n",
)
gen_rules = Prompt(
    default=f"Generate a new set of rules that builds on or revises "
            f"the current ruleset based on the above results "
            f"to improve the overall accuracy. "
            f"Format the output in the form of a rule list line by line, "
            f"with each rule in a new line, no bullet points, "
            f"and no empty lines in between.",
)
gen_experiences = Prompt(
    default=f"summarize the type(s) of error(s) you made, "
            f"if you notice multiple errors, put them in a list, "
            f"with each error in a new line with no bullet point.",
)
