from typing import Literal
from pydantic import BaseModel

class SupervisorDecision(BaseModel):
    next:Literal[
        "research",
        "writer",
        "reviewer",
        "human",
        "FINISH"
    ]