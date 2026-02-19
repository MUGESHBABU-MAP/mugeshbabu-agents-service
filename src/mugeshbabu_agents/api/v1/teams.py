from typing import List
from fastapi import APIRouter, HTTPException
from mugeshbabu_agents.domain.teams.service import team_service
from mugeshbabu_agents.domain.teams.models import Team, CreateTeamRequest
from mugeshbabu_agents.domain.agents.models import Agent

router = APIRouter()

@router.post("/", response_model=Team)
async def create_team(request: CreateTeamRequest):
    """Create a new team."""
    try:
        team = await team_service.create_team(request)
        return team
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{team_id}", response_model=Team)
async def get_team(team_id: str):
    """Get team details by ID."""
    team = await team_service.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.get("/{team_id}/agents", response_model=List[Agent])
async def get_team_agents(team_id: str):
    """Get all agents associated with a team (static + dynamic)."""
    try:
        agents = await team_service.get_team_agents(team_id)
        return agents
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
