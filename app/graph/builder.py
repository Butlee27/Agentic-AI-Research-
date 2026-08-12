from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import GraphState

from app.agents.supervisor import supervisor
from app.agents.research_agent import research_agent
from app.agents.writer_agent import writer_agent
from app.agents.reviewer_agent import reviewer_agent
from app.agents.human_approval import human_approval


def route_supervisor(state: GraphState):

    next_node = state.get("next","")

    print(
        f"\nSUPERVISOR ROUTER → {next_node}"
    )

    if next_node in {
        "research",
        "writer",
        "reviewer",
        "human",
        "FINISH",
    }:
        return next_node

    raise ValueError(
        f"Invalid supervisor decision: {next_node}"
    )


def route_human(state:GraphState):
    decision=state.get(
        "human_decision",
        ""
    )

    decision=str(
        decision
    ).strip().lower()

    print(f"\nHUMAN ROUTER → {decision}")

    if decision=="approve":
        print("HUMAN APPROVED → FINISH"
        )

        return "FINISH"


    if decision=="reject":
        print(
            "HUMAN REJECTED → SUPERVISOR"
        )

        return "supervisor"


    raise ValueError(
        f"invalid human decision:{decision}"
    )


graph = StateGraph(GraphState)


graph.add_node(
    "supervisor",
    supervisor
)

graph.add_node(
    "research",
    research_agent
)

graph.add_node(
    "writer",
    writer_agent
)

graph.add_node(
    "reviewer",
    reviewer_agent
)

graph.add_node(
    "human",
    human_approval
)



graph.add_edge(
    START,
    "research"
)


graph.add_edge(
    "research",
    "supervisor"
)


graph.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "research": "research",
        "writer": "writer",
        "reviewer": "reviewer",
        "human": "human",
        "FINISH": END,
    }
)


graph.add_edge(
    "writer",
    "supervisor"
)


graph.add_edge(
    "reviewer",
    "supervisor"
)


graph.add_conditional_edges(
    "human",
    route_human,
    {"FINISH":END,
    "supervisor":"supervisor"
    }
)


checkpointer = MemorySaver()


app = graph.compile(
    checkpointer=checkpointer
)