import logging
from typing import List, Optional
from bson import ObjectId

from mugeshbabu_agents.infrastructure.db import db_manager
from mugeshbabu_agents.domain.teams.models import Team, CreateTeamRequest
from mugeshbabu_agents.domain.agents.models import Agent

logger = logging.getLogger(__name__)

class TeamService:
    async def create_team(self, request: CreateTeamRequest) -> Team:
        """Create a new team."""
        db = db_manager.get_master_db()
        team = Team(**request.model_dump())
        result = await db.teams.insert_one(team.model_dump(by_alias=True))
        team.id = result.inserted_id
        return team

    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        db = db_manager.get_master_db()
        doc = await db.teams.find_one({"_id": ObjectId(team_id)})
        if doc:
            return Team(**doc)
        return None

    async def get_team_agents(self, team_id: str) -> List[Agent]:
        """
        Get all agents belonging to a team.
        Combines static `agent_ids` AND dynamic resolution based on filters.
        """
        team = await self.get_team(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")

        db = db_manager.get_master_db()
        agents = []

        # 1. Fetch static agents
        if team.agent_ids:
            # Convert string IDs to ObjectIds if stored as such, depends on Agent model storage
            # Assuming Agent IDs are stored as ObjectIds in DB
            static_agent_ids = [ObjectId(aid) for aid in team.agent_ids if ObjectId.is_valid(aid)]
            if static_agent_ids:
                cursor = db.agents.find({"_id": {"$in": static_agent_ids}})
                async for doc in cursor:
                    agents.append(Agent(**doc))

        # 2. Fetch dynamic agents
        if team.dynamic_filters:
            # Construct query from filters
            # e.g. filters={"category": "SAP"} -> query={"category": "SAP"}
            # We need to ensure we don't duplicate agents already found
            filter_query = team.dynamic_filters.copy()
            
            # Exclude already found IDs
            found_ids = [a.id for a in agents if a.id]
            if found_ids:
                filter_query["_id"] = {"$nin": found_ids}
            
            cursor = db.agents.find(filter_query)
            async for doc in cursor:
                agents.append(Agent(**doc))

        return agents

team_service = TeamService()
