from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from duckduckgo_search.exceptions import TimeoutException

def search_wrapper(k=1, full_text=False):
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=k)
    engine = DuckDuckGoSearchRun(api_wrapper=wrapper)
    
    def search(query):
        tries, result = 0, None
        while result is None and tries < 3:
            try:
                tries += 1
                result = engine.invoke(query)
            except TimeoutException:
                pass
        
        if result is not None:
            return result
        return 'No good search results were found.'
        
    return search
