from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_llm
from app.graph.state import GraphState


llm = get_llm()


def reviewer_agent(state: GraphState):

    print("\n>>> REVIEWER AGENT STARTED <<<")

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
            "Reviewer Agent could not find "
            "the original user question."
        )

    user_question = user_question[:3000]

    report = ""

    if messages:

        report = messages[-1].content

        if not isinstance(
            report,
            str
        ):
            report = str(
                report
            )

    if not report:

        raise ValueError(
            "Reviewer Agent did not receive "
            "a report from the Writer Agent."
        )

    report = report[:7000]


    system_prompt = SystemMessage(
        content="""
You are the Reviewer Agent in an AI Research System.

Your job is to perform a strict quality review of the
Writer Agent's report.

The ORIGINAL USER QUESTION is the most important
reference point.

You must determine whether the report actually answers
the user's question.

Review the report for:

1. QUESTION ALIGNMENT
   - Does the report directly answer the original question?
   - Does it answer all important parts of the question?

2. FACTUAL SUPPORT
   - Are the claims supported by the available research?
   - Are there unsupported or invented claims?

3. COMPLETENESS
   - Is important information missing?
   - Does the report provide enough detail for the question?

4. RELEVANCE
   - Does the report contain unnecessary or unrelated
     information?

5. CLARITY
   - Is the explanation easy to understand?
   - Are technical concepts explained appropriately?

6. STRUCTURE
   - Is the report logically organized?

7. SOURCES
   - Are useful sources included when available?
   - Are source URLs preserved correctly?

IMPORTANT:

Do NOT perform new research.

Do NOT use retrieval tools.

Do NOT invent missing information.

Do NOT discuss the internal agent workflow.

If the report is already good, preserve its content
and improve only minor clarity or formatting issues.

If the report does NOT answer the original question,
you must identify exactly what is missing or incorrect.

Your final output must be the REVIEWED REPORT.

Do not output a review score.

Do not output a separate critique.

Do not say "the report is good".

Return only the final reviewed report.
"""
    )


    review_request = HumanMessage(
        content=f"""
ORIGINAL USER QUESTION:

{user_question}

==================================================

WRITER REPORT:

{report}

==================================================

Review this report against the ORIGINAL USER QUESTION.

Make sure the final version:

- directly answers the question
- contains relevant information
- does not contain unsupported claims
- includes important technical details when required
- preserves useful sources
- removes irrelevant information
- is clear and professionally structured

Return ONLY the final reviewed report.
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

        "workflow_stage": "human",

        "completed_stage": "reviewer",

        "human_decision": "",

        "revision_reason": "",
    }