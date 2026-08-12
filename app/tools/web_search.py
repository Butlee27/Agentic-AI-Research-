import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
api_key=os.getenv("TAVILY_API_KEY")

if not api_key:
    raise ValueError(
        "TAVILY_API_KEY is not set."
        "Add it to your .env file."
    )

Tavilyclient =TavilyClient(
    api_key=api_key
)

def web_search(
        query:str,
        max_results:int=5
)-> str:
    """
    Search the web using Tavily and return
    concise research-oriented results.
    """

    response=Tavilyclient.search(
        query=query,
        search_depth="basic",
        max_results=max_results,
        include_answer=False,
    )

    results= response.get(
        "results",
        []
    )

    if not results:
        return "No web search results found."

    formatted_results=[]

    for index,result in enumerate(
        results,
        start=1
    ):
        title=result.get(
            "title",
            "untitled"
        )

        url=result.get(
            "url",
            ""
        )

        content=result.get(
            "content",
            ""
        )

        content=content[:2000]

        formatted_results.append(
            f"""
SOURCE {index}
Title:
{title}

URL:
{url}

Content:
{content}
"""
        )

        return "\n".join(formatted_results)