from typing import Literal
from pydantic import BaseModel
from app.config import get_llm

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