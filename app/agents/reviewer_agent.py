from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.config import get_llm
from app.graph.state import GraphState



llm = get_llm()


def reviewer_agent(state: GraphState):

    messages = state.get(
        "messages",
        []
    )

   
    report = ""

    if messages:

        report = messages[-1].content

        if not isinstance(
            report,
            str
        ):
            report = str(report)


  
    report = report[:7000]


  
    system_prompt = SystemMessage(
        content="""
You are the Reviewer Agent.

Your responsibility is to review the research report.

Check:

1. Factual consistency
2. Completeness
3. Relevance to the research question
4. Clarity
5. Structure
6. Technical accuracy

Do NOT perform new research.

Do NOT use retrieval tools.

Do NOT rewrite the entire report.

Return the reviewed report in polished form.

If information appears incomplete, improve the
report using only the information already provided.
"""
    )



    review_request = HumanMessage(
        content=f"""
Review the following research report:

---------------- REPORT ----------------

{report}

-------------- END REPORT --------------

Produce the reviewed and polished report.
"""
    )


   
    response = llm.invoke(
        [
            system_prompt,
            review_request,
        ]
    )

    response.name = "reviewer_agent"


    return {
        "messages": [
            response
        ],

        "workflow_stage": "reviewer",

        "completed_stage": "reviewer",
    }