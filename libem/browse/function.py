import os
import json

from langchain_google_community import GoogleSearchAPIWrapper
from langchain_core.tools import Tool

import libem

schema = {
    "type": "function",
    "function": {
        "name": "browse",
        "description": "Browse the web to find descriptions for the given entity",
        "parameters": {
            "type": "object",
            "properties": {
                "entity": {
                    "type": "string",
                    "description": "Entity description",
                },
            },
            "required": ["entity"],
        },
    }
}


def func(entity):
    return google(entity)


""" Google search function """

# Set up environment variables for Google API if they are not already set
os.environ.setdefault(
    "GOOGLE_CSE_ID",
    libem.LIBEM_CONFIG.get("GOOGLE_CSE_ID", "")
)
os.environ.setdefault(
    "GOOGLE_API_KEY",
    libem.LIBEM_CONFIG.get("GOOGLE_API_KEY", "")
)


def google(entity):
    # Ensure required environment variables are set
    if not os.environ.get("GOOGLE_CSE_ID") or not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError(f"GOOGLE_CSE_ID or GOOGLE_API_KEY is not set. "
                               f"Check your environment or {libem.LIBEM_CONFIG_FILE}.")

    tool = Tool(
        name="google_search",
        description="Search Google and return the first result.",
        func=GoogleSearchAPIWrapper(k=1).run,
    )
    desc = tool.run(entity)
    return json.dumps(
        {
            "Entity description:": desc,
        })
