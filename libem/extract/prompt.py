from libem.core.struct import Prompt

role = Prompt(
    default="You are a named entity recognizer.",
)

query = Prompt(
    default="What are the entities in '{desc}'?",
)

output = Prompt(
    default='Output the entities in the format of JSON, enclosed by """.',
)