import json
from libem.browse import prompt
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
                "entity": {
                    "type": "string",
                    "description": "Entity description",
                },
                "engine": {
                    "type": "string",
                    "description": "The search engine to use. Choose from "
                                    "['google', 'duckduckgo'], default is "
                                    "'duckduckgo'.",
                },
            },
            "required": ["entity"],
        },
    }
}

engines_map = {
    'google': google_search,
    'duckduckgo': duckduckgo_search
}


def func(entity, engine='duckduckgo'):
    serch_engine = engines_map[engine]
    
    tool = Tool(
        name="online_search",
        description="Search the internet and return the first result if available.",
        func=serch_engine(k=1, full_text=False),
    )
    desc = tool.run(entity)
    return json.dumps(
        {
            "Entity description:": desc,
        })
