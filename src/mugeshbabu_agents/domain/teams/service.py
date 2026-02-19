import logging
from typing import List, Optional
from bson import ObjectId

from mugeshbabu_agents.infrastructure.db import db_manager
from mugeshbabu_agents.domain.teams.models import Team, CreateTeamRequest
from mugeshbabu_agents.domain.agents.models import Agent

logger = logging.getLogger(__name__)
from mugeshbabu_agents.infrastructure.repository import BaseRepository

logger = logging.getLogger(__name__)

class TeamRepository(BaseRepository[Team]):
    pass

class TeamService:
    def __init__(self):
        # We'll initialize repo on demand or in dependency injection
        pass

    async def create_team(self, request: CreateTeamRequest) -> Team:
        """Create a new team."""
        db = db_manager.get_master_db()
        repo = TeamRepository(db, "teams", Team)
        
        team = Team(**request.model_dump())
        return await repo.create(team)

    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        db = db_manager.get_master_db()
        repo = TeamRepository(db, "teams", Team)
        return await repo.get(team_id)

    async def get_team_agents(self, team_id: str) -> List[Agent]:
        """
        Get all agents belonging to a team.
        Combines static `agent_ids` AND dynamic resolution based on filters.
        """
        team = await self.get_team(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")

        db = db_manager.get_master_db()
        # Agents might not have a dedicated repository yet if they are just mocked,
        # but let's assume we can access the 'agents' collection.
        # For this complex query, we might still use direct DB or extend Repository.
        
        agents = []

        # 1. Fetch static agents
        if team.agent_ids:
            static_agent_ids = [ObjectId(aid) for aid in team.agent_ids if ObjectId.is_valid(aid)]
            if static_agent_ids:
                cursor = db.agents.find({"_id": {"$in": static_agent_ids}})
                async for doc in cursor:
                    agents.append(Agent(**doc))

        # 2. Fetch dynamic agents
        if team.dynamic_filters:
            filter_query = team.dynamic_filters.copy()
            found_ids = [a.id for a in agents if a.id]
            if found_ids:
                filter_query["_id"] = {"$nin": found_ids}
            
            cursor = db.agents.find(filter_query)
            async for doc in cursor:
                agents.append(Agent(**doc))

        return agents

team_service = TeamService()
