import typing

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


def search(k=1, full_text=False) -> typing.Callable:
    _ = full_text

    wrapper = DuckDuckGoSearchAPIWrapper(max_results=k)
    search = DuckDuckGoSearchRun(api_wrapper=wrapper)

    return search
