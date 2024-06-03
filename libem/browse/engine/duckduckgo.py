from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

def search_wrapper(k=1, full_text=False):
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=k)
    search = DuckDuckGoSearchRun(api_wrapper=wrapper)
        
    return search
