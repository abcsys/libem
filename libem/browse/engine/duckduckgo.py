from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from duckduckgo_search.exceptions import TimeoutException

def search_wrapper(k=1, full_text=False):
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=k)
    engine = DuckDuckGoSearchRun(api_wrapper=wrapper)
    
    def search(query):
        result = None
        # try again if encounters timeout exception
        try:
            result = engine.invoke(query)
        except TimeoutException:
            result = engine.invoke(query)
        
        if result is not None:
            return result
        return 'No good search results were found.'
        
    return search
