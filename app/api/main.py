from typing import Any
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.graph.builder import app as research_app


api=FastAPI(
    title="AI Research Agent API",
    description=(
        "AI Research Agent powered by"
        "Langgraph,MCP and FastAPI."
    ),
    version="1.0.0"
)

class ResearchRequest(BaseModel):
    question:str=Field(
        min_length=3,
        description="Research question"
    )

class HumanDecisionRequest(BaseModel):
    decision:str=Field(
        default="",
        description="Reason required when rejecting"
    )
    revision_reason:str=""

def get_config(thread_id:str):
    return {
        "configurable":{
            "thread_id":thread_id
        }
    }

def get_interrupt_data(result:dict):
    interrupts=result.get(
        "__interrupt__",
        []
    )

    if not interrupts:
        return None

    interrupt_value=interrupts[0].value
    return interrupt_value

def get_final_report(result:dict):
    messages=result.get(
        "messages",
        []
    )

    if not messages:
        return ""

    return str(
        messages[-1].content
    )

@api.get("/")
def root():
    return {
        "status":"online",
        "service":"AI Research Agent"
    }

@api.post("/research")
def start_research(
        request:ResearchRequest
):
    import uuid

    thread_id=str(
        uuid.uuid4()
    )

    config=get_config(
        thread_id
    )

    initial_state={
        "messages":[
            HumanMessage(
                content=request.question
            )
        ],

        "workflow_stage":"research",
        "completed_stage":"",
        "human_decision":"",
        "revision_reason":"",
        "next":""  
    }


    try:

        result=research_app.invoke(
            initial_state,
            config=config
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    interrupt_data=(get_interrupt_data(
        result
    ))


    if interrupt_data:
        return {
            "status":"waiting_for_approval",
            "thread_id":thread_id,
            "approval":interrupt_data
        }

    return {
        "status":"completed",
        "thread_id":thread_id,
        "report":get_final_report(result)
    }




@api.post(
    "/research/{thread_id}/decision"
)

def human_decision(
    thread_id:str,
    request:HumanDecisionRequest
):
    decision=request.decision.lower().strip()
    print("\n==============================")
    print("RESUMING WORKFLOW")
    print("==============================")
    print("Thread ID:", thread_id)
    print("Decision:", decision)
    print("Revision reason:", request.revision_reason)
    print("==============================\n")

    if decision not in {
        "approve",
        "reject"
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Decision must be 'approve' or 'reject'."
            )
        )

    if (decision=="reject"
        and not request.revision_reason.strip()):

        raise HTTPException(
            status_code=400,
            detail=(
                "A rejection reason is required."
            )
        )

    config=get_config(
        thread_id
    )

    resume_value={
        "decision":decision,
        "reason":request.revision_reason
    }


    try:
        result=research_app.invoke(
            Command(
                resume=resume_value
            ),
            config=config
        )


    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    interrupt_data=(
        get_interrupt_data(
            result
        )
    )

    if interrupt_data:

        print("\n==============================")
        print("HUMAN APPROVAL REQUIRED")
        print("==============================")
        print("THREAD ID:", thread_id)
        print("==============================\n")
        return {
            "status":"waiting_for_approval",
            "thread_id":thread_id,
            "approval":interrupt_data
        }

    return {
        "status":"completed",
        "thread_id":thread_id,
        "report":get_final_report(result)
    }