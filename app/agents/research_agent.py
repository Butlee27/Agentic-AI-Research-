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

Your job is to gather reliable evidence that directly answers
the user's research question.

You have two sources:

1. LIVE WEB SEARCH
   - Current and external information.
   - Useful for recent, latest, current, or time-sensitive questions.
   - Preserve useful URLs.

2. INTERNAL KNOWLEDGE BASE
   - Information from the project's internal documents.
   - Use it when relevant to the user's question.
   - It may contain no relevant information for some questions.

IMPORTANT:

The user's original question is the PRIMARY objective.

Do NOT simply summarize the retrieved information.

Instead:

1. Identify exactly what the user is asking.
2. Extract information from the sources that directly answers it.
3. Remove irrelevant search results.
4. Prefer specific evidence over generic explanations.
5. Use web information when current/external information is required.
6. Use internal knowledge when project-specific information is relevant.
7. If the knowledge base contains no relevant context, explicitly state:
   "No relevant internal knowledge-base context was found."
8. If web search contains no useful result, explicitly state:
   "No useful web result was found."
9. Never invent missing information.
10. Preserve source URLs from web results.
11. Clearly separate WEB SOURCES and INTERNAL SOURCES.

Return research notes in this structure:

RESEARCH QUESTION:
<original question>

ANSWER REQUIREMENTS:
<what must be answered>

KEY FINDINGS:
<facts that directly answer the question>

TECHNICAL DETAILS:
<important technical information>

WEB SOURCES:
<relevant web findings and URLs>

INTERNAL SOURCES:
<relevant knowledge-base findings>

LIMITATIONS:
<missing information, uncertainty, or unavailable context>

Do NOT write the final report.
Do NOT add generic information that does not help answer the question.
"""
    )

    synthesis_request = HumanMessage(
        content=f"""
ORIGINAL USER QUESTION:

{user_question}


WEB SEARCH RESULTS:

{web_result}


INTERNAL KNOWLEDGE BASE RESULTS:

{knowledge_result}


Analyze these sources specifically for the original
user question.

Return research notes using the required structure.
Only include information that helps answer the question.
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