import os
import yaml

from langchain.schema import BaseOutputParser


# Read OpenAI key from ~/.libem/config.yaml
def get_openai_api_key():
    with open(os.path.expanduser("~/.libem/config.yaml"), "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
        if "openai_api_key" not in config:
            raise Exception("OpenAI API key not found in ~/.libem/config.yaml,"
                            " please add 'openai_api_key: YOUR_KEY' in the file.")
        openai_api_key = config["openai_api_key"]
        return openai_api_key


class CommaSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, ans):
        ret = []
        ans = ans.strip()[1:-1].split(",")
        for an in ans:
            ret.append(an.strip()[1:-1])

        return ret
