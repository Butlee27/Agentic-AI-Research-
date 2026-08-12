from app.graph.state import GraphState



VALID_TRANSITIONS = {

    "research": {
        "research",
        "writer",
    },


    "writer": {
        "writer",
        "reviewer",
        "research",
    },


    "reviewer": {
        "reviewer",
        "writer",
        "research",
        "FINISH",
    },



    "human": {
        "research",
        "writer",
        "reviewer",
        "FINISH",
    },
}


def validate_supervisor_decision(
    state: GraphState,
    decision: str
):

    current_stage = state.get(
        "workflow_stage",
        "research"
    )

    allowed_destinations = VALID_TRANSITIONS.get(
        current_stage,
        set()
    )

    if decision not in allowed_destinations:

        raise ValueError(
            f"Invalid Supervisor transition: "
            f"{current_stage} → {decision}. "
            f"Allowed transitions: "
            f"{sorted(allowed_destinations)}"
        )

    return decision