import os
import requests
import typing

from bs4 import BeautifulSoup
from bs4.element import Comment
from googleapiclient.discovery import build

import libem


def search(k=1, full_text=False) -> typing.Callable:
    # Set up environment variables for Google API if they are not already set
    os.environ.setdefault(
        "GOOGLE_CSE_ID",
        libem.LIBEM_CONFIG.get("GOOGLE_CSE_ID", "")
    )
    os.environ.setdefault(
        "GOOGLE_API_KEY",
        libem.LIBEM_CONFIG.get("GOOGLE_API_KEY", "")
    )

    # Ensure required environment variables are set
    if not os.environ.get("GOOGLE_CSE_ID") or not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError(f"GOOGLE_CSE_ID or GOOGLE_API_KEY is not set. "
                               f"Check your environment or {libem.LIBEM_CONFIG_FILE}.")

    # google search api
    service = build("customsearch", "v1", developerKey=os.environ.get("GOOGLE_API_KEY"))

    def search_func(query):
        # Helper functions to extract full text from a webpage
        headers = {
            'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        }

        def tag_visible(element):
            if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
                return False
            if isinstance(element, Comment):
                return False
            return True

        def text_from_html(url):
            try:
                body = requests.get(url, headers=headers).text
            except requests.exceptions.RequestException:
                return 'Error fetching webpage.'

            soup = BeautifulSoup(body, 'html.parser')
            texts = soup.findAll(string=True)
            visible_texts = filter(tag_visible, texts)
            text = u" ".join(t.strip() for t in visible_texts)
            if len(text) > 5000:
                return text[0:5000]
            return text

        res = service.cse().list(q=query, cx=os.environ.get("GOOGLE_CSE_ID"), num=k).execute()
        pages = res.get('items', [])

        if len(pages) == 0:
            return 'No good Google Search Result was found.'

        if full_text:
            return "\n".join([text_from_html(p['link']) for p in pages])
        else:
            return "\n".join([p['snippet'] for p in pages if 'snippet' in p])

    return search_func
