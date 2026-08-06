from langchain_core.tools import tool

@tool
def retrieve_documents(query:str)-> str:
    """
    Retrieve relevant information from the specified sources.
    Args:
        source:Source of information (pdf,github,filesystem,google_drive)
        query:User research query
        
    returns:
        Relevant research information.
        """

    return f"""
Research Result:
"""