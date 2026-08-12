from langchain_core.tools import tool
from app.retrieval.pipeline import retrieve_documents

@tool
def retrieval_tool(query:str)-> str:
    """
    Retrieve relevant information for a research query.
    Use this tool whenever external information is required before answering.
    """

    return retrieve_documents(query)