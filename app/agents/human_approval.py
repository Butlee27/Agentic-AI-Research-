from langgraph.types import interrupt

from app.graph.state import GraphState


def human_approval(state: GraphState):

    print("\n>>> HUMAN APPROVAL NODE <<<")

    # Get the current report
    messages = state.get("messages", [])

    report = ""

    if messages:
        report = str(messages[-1].content)

    # Pause the graph
    human_response = interrupt(
        {
            "type": "human_approval",

            "message": """
The Reviewer has completed the report.

Please review the report and decide:

APPROVE
or
REJECT

If rejecting, provide a reason explaining
what needs to be improved.
""",

            "report": report,
        }
    )

    print("\n>>> HUMAN NODE RESUMED <<<")
    print("Human response:", human_response)

    decision = ""
    revision_reason = ""

    if isinstance(human_response, dict):

        decision = str(
            human_response.get(
                "decision",
                ""
            )
        ).lower().strip()

        revision_reason = str(
            human_response.get(
                "reason",
                ""
            )
        ).strip()

    else:

        decision = str(
            human_response
        ).lower().strip()

    print("Decision:", decision)
    print("Revision reason:", revision_reason)

    if decision not in {
        "approve",
        "reject",
    }:

        raise ValueError(
            f"Invalid human decision: {decision}"
        )

    return {
        "workflow_stage": "human",
        "human_decision": decision,
        "revision_reason": revision_reason,
    }