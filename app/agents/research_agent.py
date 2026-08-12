import asyncio
import threading

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.config import get_llm
from app.graph.state import GraphState

from app.mcp.client import (
    search_web,
    search_research_knowledge,
)


llm = get_llm()

def run_async(coro):
    """
    Run an async MCP function from a synchronous
    LangGraph node.
    """

    try:
        loop = asyncio.get_running_loop()

    except RuntimeError:
        loop = None


   
    if loop and loop.is_running():

        result = {}

        def runner():

            result["value"] = asyncio.run(coro)


        thread = threading.Thread(
            target=runner
        )

        thread.start()
        thread.join()

        return result["value"]



    return asyncio.run(coro)


def mcp_web_search(
    query: str
) -> str:

    """
    Search the live web through MCP.

    Reduced from 5 results to 3 to decrease
    latency and LLM context size.
    """

    return run_async(
        search_web(
            query=query,
            max_results=3,
        )
    )


def mcp_knowledge_search(
    query: str
) -> str:

    """
    Search the project's internal research
    knowledge base through MCP.
    """

    return run_async(
        search_research_knowledge(
            query=query,
        )
    )


async def parallel_research_search(
    query: str
):
    """
    Run Web Search and Knowledge Base Search
    concurrently.

    Before:

        Web Search
             ↓
        Knowledge Search

    Now:

        Web Search ─────┐
                        ├──→ Results
        Knowledge ──────┘

    This reduces total waiting time.
    """

    web_task = asyncio.create_task(
        search_web(
            query=query,
            max_results=3,
        )
    )

    knowledge_task = asyncio.create_task(
        search_research_knowledge(
            query=query,
        )
    )


    web_result, knowledge_result = (
        await asyncio.gather(
            web_task,
            knowledge_task,
            return_exceptions=True,
        )
    )



    if isinstance(
        web_result,
        Exception
    ):

        print(
            "Web search failed:",
            web_result
        )

        web_result = (
            "Web search failed. "
            "No web results available."
        )


    if isinstance(
        knowledge_result,
        Exception
    ):

        print(
            "Knowledge base search failed:",
            knowledge_result
        )

        knowledge_result = (
            "Knowledge base search failed. "
            "No internal results available."
        )


    return (
        str(web_result),
        str(knowledge_result),
    )



def research_agent(
    state: GraphState
):

    print(
        "\n>>> RESEARCH AGENT STARTED <<<"
    )


    messages = state.get(
        "messages",
        []
    )


    user_question = ""


    for message in messages:

        if isinstance(
            message,
            HumanMessage
        ):

            user_question = str(
                message.content
            )

            break


    if not user_question:

        raise ValueError(
            "Research Agent could not find "
            "the user's research question."
        )



    user_question = user_question[:2000]


    print(
        "\nResearch question:"
    )

    print(
        user_question
    )


    print(
        "\n>>> MCP PARALLEL SEARCH <<<"
    )

    print(
        "Running Web Search + Knowledge Base Search..."
    )


    try:

        web_result, knowledge_result = run_async(
            parallel_research_search(
                user_question
            )
        )

    except Exception as exc:

        print(
            "Parallel MCP search failed:",
            exc
        )

        web_result = (
            "Web search failed."
        )

        knowledge_result = (
            "Knowledge base search failed."
        )


    web_result = str(
        web_result
    )[:2500]


    knowledge_result = str(
        knowledge_result
    )[:2500]


    print(
        "\nWeb context size:",
        len(web_result)
    )

    print(
        "Knowledge context size:",
        len(knowledge_result)
    )


    research_prompt = SystemMessage(
        content="""
You are the Research Agent in an AI Research System.

Your job is to analyze information collected from:

1. LIVE WEB SEARCH
2. INTERNAL RESEARCH KNOWLEDGE BASE

The Writer Agent will use your research notes
to create the final report.

Your responsibilities:

- Identify important facts.
- Combine relevant information from both sources.
- Prefer reliable and relevant information.
- Do not invent facts.
- Clearly distinguish information when sources disagree.
- Preserve useful source URLs from web results.
- Remove irrelevant information.
- Organize the findings into useful research notes.

The research notes should contain:

1. Key findings
2. Important technical details
3. Supporting information
4. Sources / URLs when available
5. Important limitations or uncertainty

Do NOT write the final report.

Do NOT add an unnecessary introduction or conclusion.

Return concise but sufficiently detailed research notes.
"""
    )

    synthesis_request = HumanMessage(
        content=f"""
USER RESEARCH QUESTION:

{user_question}


WEB SEARCH RESULTS:

{web_result}


INTERNAL KNOWLEDGE BASE RESULTS:

{knowledge_result}


Analyze both sources and produce
concise, high-quality research notes
for the Writer Agent.
"""
    )


    response = llm.invoke(
        [
            research_prompt,
            synthesis_request,
        ]
    )


    response.name = (
        "research_agent"
    )


   
    return {

        "messages": [
            response
        ],

        "workflow_stage": "research",

        "completed_stage": "research",

        "human_decision": "",

        "revision_reason": "",
    }