from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_llm
from app.graph.state import GraphState


llm = get_llm()

def writer_agent(state: GraphState):

    messages = state.get(
        "messages",
        []
    )


    research_notes = ""

    if messages:

        research_notes = messages[-1].content

        if not isinstance(
            research_notes,
            str
        ):
            research_notes = str(
                research_notes
            )

   
    research_notes = research_notes[:7000]


    system_prompt = SystemMessage(
        content="""
You are the Writer Agent.

Your responsibility is to create a professional
research report from the research notes provided.

The report should:

1. Have a clear title.
2. Begin with an introduction.
3. Explain the important concepts clearly.
4. Organize information using useful headings.
5. Use the available research accurately.
6. Avoid inventing unsupported facts.
7. End with a concise conclusion.

Do not perform new research.

Do not use retrieval tools.

Do not discuss the agent workflow.

Return only the completed research report.
"""
    )



    writer_request = HumanMessage(
        content=f"""
Create a professional research report using
the following research notes:

---------------- RESEARCH NOTES ----------------

{research_notes}

-------------- END RESEARCH NOTES ---------------

Write the final report now.
"""
    )



    response = llm.invoke(
        [
            system_prompt,
            writer_request,
        ]
    )


    response.name = "writer_agent"



    return {
        "messages": [
            response
        ],

        "workflow_stage": "writer",

        "completed_stage": "writer",

        "human_decision":"",

        "revision_reason":""
    }