from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_llm
from app.graph.state import GraphState


llm = get_llm()


def writer_agent(state: GraphState):

    messages = state.get(
        "messages",
        []
    )

    user_question = ""

    for message in messages:

        if isinstance(
            message,
            HumanMessage
        ):

            user_question = str(
                message.content
            )

            break

    if not user_question:

        raise ValueError(
            "Writer Agent could not find "
            "the original user question."
        )

    user_question = user_question[:3000]


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
You are the Writer Agent in an AI Research System.

Your PRIMARY responsibility is to directly answer
the user's original research question.

The research notes were collected specifically to
help answer that question.

IMPORTANT RULES:

1. Read the ORIGINAL USER QUESTION carefully.

2. The final report MUST directly answer that question.

3. Do not simply summarize the research notes.

4. Use only information supported by the research notes.

5. Do not invent facts, sources, statistics, or claims.

6. Remove information that is irrelevant to the
   original question.

7. If the research notes do not contain enough
   information to answer an important part of the
   question, clearly state that the information
   was not available.

8. Preserve useful source URLs from the research notes.

9. Do not perform new research.

10. Do not use retrieval tools.

11. Do not discuss the internal agent workflow.

12. Do not mention "retrieved context", "context
    window", or internal processing.

13. Give a clear and useful answer rather than
    merely describing the sources.

STRUCTURE THE REPORT AS:

# Direct Answer

Give a clear answer to the user's question first.

# Detailed Explanation

Explain the important concepts required to fully
understand the answer.

# Key Points

List the most important findings.

# Technical Details

Include technical information when relevant to
the question.

# Sources

List the useful source URLs available in the
research notes.

# Limitations

Mention important missing information or uncertainty
only when it actually exists.

Do not force sections that are not useful for the
question.

Return ONLY the completed research report.
"""
    )


    writer_request = HumanMessage(
        content=f"""
ORIGINAL USER QUESTION:

{user_question}

==================================================

RESEARCH NOTES:

{research_notes}

==================================================

Write a professional research report that directly
answers the ORIGINAL USER QUESTION.

The original question is the highest priority.

Do not add unrelated information simply because it
appears in the research notes.

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

        "human_decision": "",

        "revision_reason": ""
    }