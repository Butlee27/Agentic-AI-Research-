from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_llm
from app.graph.state import GraphState


supervisor_llm = get_llm()


def supervisor(state: GraphState):

    workflow_stage = state.get(
        "workflow_stage",
        "research"
    )

    completed_stage = state.get(
        "completed_stage",
        ""
    )

    human_decision = state.get(
        "human_decision",
        ""
    )

    revision_reason = state.get(
        "revision_reason",
        ""
    )

    workflow_stage = str(
        workflow_stage
    ).strip().lower()

    completed_stage = str(
        completed_stage
    ).strip().lower()

    human_decision = str(
        human_decision
    ).strip().lower()

    revision_reason = str(
        revision_reason
    ).strip()


    print("\n===================================")
    print("SUPERVISOR")
    print("Current stage:", workflow_stage)
    print("Completed stage:", completed_stage)
    print("Human decision:", human_decision)

    if revision_reason:
        print(
            "Revision reason:",
            revision_reason
        )


    if human_decision == "approve":

        print(
            "Validated decision: FINISH"
        )

        print(
            "===================================\n"
        )

        return {
            "next": "FINISH",
            "workflow_stage": "FINISH",
        }



    if human_decision == "reject":

        prompt = SystemMessage(
            content="""
You are the supervisor of an AI research workflow.

The human rejected the report.

Determine which stage needs revision.

Choose exactly ONE:

research
writer
reviewer

Use these rules:

research:
The research lacks facts, evidence, sources,
technical information, or important content.

writer:
The research is sufficient but the report needs
better structure, clarity, organization, or explanation.

reviewer:
The report should undergo another quality review.

Return ONLY:
research
writer
reviewer
"""
        )


        request = HumanMessage(
            content=f"""
Completed stage:
{completed_stage}

Human revision reason:
{revision_reason}
"""
        )


        try:

            response = supervisor_llm.invoke(
                [
                    prompt,
                    request,
                ]
            )

            llm_decision = str(
                response.content
            ).strip().lower()


        except Exception as exc:

            print(
                "Supervisor LLM error:",
                exc
            )

            llm_decision = "writer"


    
        if "research" in llm_decision:

            next_stage = "research"

        elif "writer" in llm_decision:

            next_stage = "writer"

        elif "reviewer" in llm_decision:

            next_stage = "reviewer"

        else:

            next_stage = "writer"


        print(
            "LLM revision decision:",
            next_stage
        )

        print(
            "Validated decision:",
            next_stage
        )

        print(
            "===================================\n"
        )


        return {

            "next": next_stage,

            "workflow_stage": next_stage,

        
            "human_decision": "",

            "revision_reason": "",

        }


    if not completed_stage:

        print(
            "Validated decision: research"
        )

        print(
            "===================================\n"
        )

        return {

            "next": "research",

            "workflow_stage": "research",

        }


    if completed_stage == "research":

        print(
            "Validated decision: writer"
        )

        print(
            "===================================\n"
        )

        return {

            "next": "writer",

            "workflow_stage": "writer",

        }

    if completed_stage == "writer":

        print(
            "Validated decision: reviewer"
        )

        print(
            "===================================\n"
        )

        return {

            "next": "reviewer",

            "workflow_stage": "reviewer",

        }


    if completed_stage == "reviewer":

        print(
            "Validated decision: human"
        )

        print(
            "===================================\n"
        )

        return {

            "next": "human",

            "workflow_stage": "human",

        }


    print(
        "Validated decision: FINISH"
    )

    print(
        "===================================\n"
    )

    return {

        "next": "FINISH",

        "workflow_stage": "FINISH",

    }