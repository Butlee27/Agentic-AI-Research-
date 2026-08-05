from langgraph.graph import MessagesState
class GraphState(MessagesState):
    next:str
    approved:bool
    report_type:str
    source:str

    