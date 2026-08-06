from typing import Literal
from pydantic import BaseModel
from langchain_core.messages import SystemMessage
from app.config import get_llm
from app.graph.state import GraphState

llm=get_llm()


class SupervisorDecision(BaseModel):

    next: Literal[
        "research",
        "writer",
        "reviewer",
        "human",
        "FINISH"
    ]

structured_llm=llm.with_structured_output(SupervisorDecision)


def supervisor(state: GraphState):

    system_prompt = """
You are the Supervisor of an Agentic AI Research Platform.

Your responsibility is ONLY to decide
which worker should execute next.

Available workers:

1. research
   - Collect information.
   - Use retrieval tools when needed.
   - Never write the final report.

2. writer
   - Use the research notes.
   - Produce a professional report.
   - Never perform new research.

3. reviewer
   - Review the report.
   - Improve clarity, grammar and correctness.
   - Never perform new research.

4. human
   - Ask the user for approval.

Rules:

- Read the conversation history.
- Agent messages include their agent name.
- Use those names to determine which workers have already completed their work before selecting the next worker.
- Select ONLY one next worker.
- If the workflow is complete,
  return FINISH.

Return ONLY according to the schema.
"""

    response = structured_llm.invoke(

        [
            SystemMessage(content=system_prompt)
        ]

        + state["messages"]

    )

    return {

        "next": response.next

    }