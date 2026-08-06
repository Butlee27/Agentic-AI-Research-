from langgraph.graph import MessagesState

class GraphState(MessagesState):
    """
    Shared state across the entire graph.

    Inherits MessagesState to automatically
    manage conversation history.

    Additional fields can be added as the
    project grows.
    """


    next:str
    approved:bool
    report_type:str
    source:str

    