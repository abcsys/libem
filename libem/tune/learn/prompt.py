from libem.core.struct import Prompt

recap_success = Prompt(
    default="You achieve successes on entity matching "
            "in the following examples: {successes}",
)
gen_rules = Prompt(
    default=f"generate rules to follow from the mistakes,"
            f"in the form of a rule list line by line,"
            f"with each rule in a new line with no bullet point.",
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
