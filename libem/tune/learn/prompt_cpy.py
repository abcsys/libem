from libem.core.struct import Prompt
from libem.match.prompt import rule as match_rule_prompt

recap_success = Prompt(
    default="You achieve successes on entity matching "
            "in the following examples: {successes}",
)
gen_rules = Prompt(
    default=f"**Current ruleset:**\n"
            f"{match_rule_prompt}"
            "given the mistakes you made and the current ruleset, "
            "generate an additional list of rules to follow in the future to address these mistakes.",
)
recap_mistake = Prompt(
    default="You made mistakes on entity matching "
            "in the following examples: {mistakes}",
)
gen_experiences = Prompt(
    default=f"summarize the type(s) of error(s) you made,"
            f"if you notice multiple errors, put them in a list,"
            f"with each error in a new line with no bullet point.",
)