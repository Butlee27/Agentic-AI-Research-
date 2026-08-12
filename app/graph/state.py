from langgraph.graph import MessagesState

class GraphState(MessagesState):
    next:str
    workflow_stage:str
    completed_stage:str
    human_decision:str
    revision_reason:str
