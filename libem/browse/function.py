import os
import json

from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool

from libem.constant import LIBEM_CONFIG

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

# if os env is not set, set it
if os.environ.get("GOOGLE_CSE_ID") is None:
    os.environ["GOOGLE_CSE_ID"] = LIBEM_CONFIG.get("google_cse_id", "")
if os.environ.get("GOOGLE_API_KEY") is None:
    os.environ["GOOGLE_API_KEY"] = LIBEM_CONFIG.get("google_api_key", "")


def google(entity):
    assert os.environ.get("GOOGLE_CSE_ID", "") != "", \
        "GOOGLE_CSE_ID is not set, you can set it in the environment or in the config file"
    assert os.environ.get("GOOGLE_API_KEY", "") != "", \
        "GOOGLE_API_KEY is not set, you can set it in the environment or in the config file"

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
