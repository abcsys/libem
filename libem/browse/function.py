import json
from libem.browse import prompt, parameter
from libem.core.struct import Prompt
from langchain_core.tools import Tool

from libem.browse.engine import (google_search, duckduckgo_search)

schema = {
    "type": "function",
    "function": {
        "name": "browse",
        "description": Prompt.join(
            prompt.description(), prompt.rule()
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query to search.",
                },
            },
            "required": ["query"],
        },
    }
}

engines_map = {
    'google': google_search,
    'duckduckgo': duckduckgo_search
}


def func(query):
    serch_engine = engines_map[parameter.engine()]
    
    tool = Tool(
        name="online_search",
        description="Search the internet and return up to 3 results if available.",
        func=serch_engine(k=3, full_text=False),
    )
    desc = tool.run(query)
    return desc
