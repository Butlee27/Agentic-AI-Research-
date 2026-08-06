from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from app.config import get_llm
from app.graph.state import GraphState
from app.retrieval.pipeline import retrieve_documents


@tool
def retrieval_tool(query: str) -> str:
    """
    Retrieve relevant information for a research query.
    """
    return retrieve_documents(query)


llm = get_llm()

llm_with_tools = llm.bind_tools([retrieval_tool])


def research_agent(state: GraphState):

    response = llm_with_tools.invoke(state["messages"])

    response.name="research_agent"
    return {
        "messages": [response]
    }