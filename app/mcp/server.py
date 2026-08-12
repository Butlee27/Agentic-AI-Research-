from mcp.server import MCPServer

from app.tools.retrieval_tool import retrieval_tool
from app.tools.web_search import web_search


mcp = MCPServer(
    "Agentic AI Research MCP Server"
)


@mcp.tool()
def search_research_knowledge(
    query: str
) -> str:
    """
    Search the research knowledge base and return
    relevant information for the given query.
    """

    result = retrieval_tool.invoke(
        {
            "query": query
        }
    )

    return str(result)


@mcp.tool()
def search_web(
    query:str,
    max_results:int=5
)-> str:
    """
    Search the live web for current research information.
    Returns relevant sources including titles,URLs,
    and content snippets."""


    return web_search(
        query=query,
        max_results=max_results
    )
if __name__ == "__main__":

    mcp.run(
        transport="stdio"
    )