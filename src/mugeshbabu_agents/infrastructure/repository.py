from typing import TypeVar, Generic, Optional, List, Any, Dict
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model_cls: type[T]):
        self.collection = db[collection_name]
        self.model_cls = model_cls

    async def create(self, item: T) -> T:
        """Insert a new item."""
        data = item.model_dump(by_alias=True, exclude_none=True)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
            
        result = await self.collection.insert_one(data)
        
        # If the model has an 'id' field, update it with the inserted_id
        if hasattr(item, "id"):
            item.id = result.inserted_id
            
        return item

    async def get(self, id: str | ObjectId) -> Optional[T]:
        """Get an item by ID."""
        if isinstance(id, str):
            if not ObjectId.is_valid(id):
                return None
            id = ObjectId(id)
            
        doc = await self.collection.find_one({"_id": id})
        if doc:
            return self.model_cls(**doc)
        return None

    async def list(self, filter: Dict[str, Any] = None, limit: int = 100, skip: int = 0) -> List[T]:
        """List items with optional filter."""
        if filter is None:
            filter = {}
            
        cursor = self.collection.find(filter).skip(skip).limit(limit)
        items = []
        async for doc in cursor:
            items.append(self.model_cls(**doc))
        return items

    async def update(self, id: str | ObjectId, update_data: Dict[str, Any]) -> Optional[T]:
        """Update an item by ID."""
        if isinstance(id, str):
            id = ObjectId(id)
            
        result = await self.collection.update_one(
            {"_id": id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get(id)
        return None

    async def delete(self, id: str | ObjectId) -> bool:
        """Delete an item by ID."""
        if isinstance(id, str):
            id = ObjectId(id)
            
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0
