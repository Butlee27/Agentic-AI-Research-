from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=[
        "-m",
        "app.mcp.server",
    ],
)

async def call_mcp_tool(
        tool_name:str,
        arguments:dict) -> str:
    """
    Connect to the MCP server and call a tool.
    """

    async with stdio_client(
        SERVER_PARAMS
    ) as (read,write):

        async with ClientSession(
            read,
            write
        ) as session:

            await session.initialize()
            result=await session.call_tool(
                tool_name,
                arguments
            )

            if not result.content:
                return ""

            texts=[]

            for item in result.content:

                if hasattr(item,"text"):
                    texts.append(item.text)

            return "\n".join(texts)

        
async def search_research_knowledge(
    query: str
) -> str:

    return await call_mcp_tool(
        "search_research_knowledge",
        {"query":query}
    )

async def search_web(
        query:str,
        max_results:int=5
)-> str:

    return await call_mcp_tool(
        "search_web",
        {"query":query,
         "max_results":max_results}
    )