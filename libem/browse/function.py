from langchain_core.tools import Tool

import libem
from libem.browse import prompt, parameter
from libem.core.struct import Prompt

from libem.browse.engines import (
    google,
    duckduckgo,
)

schema = {
    "type": "function",
    "function": {
        "name": "browse",
        "description": Prompt.join(
            prompt.description(),
            prompt.rules()
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query.",
                },
            },
            "required": ["query"],
        },
    }
}

engines = {
    'google': google,
    'duckduckgo': duckduckgo,
}


def func(query):
    engine = engines[parameter.engine()]

    libem.info(f"[browse] search {parameter.engine()} using query: {query}")

    tool = Tool(
        name="online_search",
        description="Search the web and return up to 3 results if available.",
        func=engine.search(k=3, full_text=False),
    )
    desc = tool.run(query)

    libem.info(f"[browse] search {parameter.engine()} returns: {desc}")

    return desc
