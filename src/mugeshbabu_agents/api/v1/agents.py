from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Depends
from mugeshbabu_agents.domain.agents.service import agent_service
from mugeshbabu_agents.domain.agents.models import AgentInstance

router = APIRouter()

@router.post("/execute/{master_agent_id}", response_model=AgentInstance)
async def execute_agent_endpoint(
    master_agent_id: str,
    payload: Dict[str, Any],
    project_id: str = "default-project" # In real app, extract from JWT/Header
):
    """
    Execute an agent by ID.
    """
    try:
        # Assuming payload contains 'input_data'
        input_data = payload.get("input_data", payload)
        
        instance = await agent_service.execute_agent(
            master_agent_id=master_agent_id,
            project_id=project_id,
            input_data=input_data
        )
        return instance
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
