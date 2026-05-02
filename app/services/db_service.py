import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class DatabaseService:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client["sukoon_db"]
        self.chats = self.db["chats"]
        self.messages = self.db["messages"]

    async def save_message(self, session_id: str, role: str, content: str, mood: str = None, user_id: str = None):
        message_doc = {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "mood": mood,
            "timestamp": datetime.utcnow()
        }
        await self.messages.insert_one(message_doc)

    async def get_chat_history(self, session_id: str, user_id: str = None):
        query = {"session_id": session_id}
        if user_id:
            query["user_id"] = user_id
        cursor = self.messages.find(query).sort("timestamp", 1)
        history = []
        async for doc in cursor:
            history.append({"role": doc["role"], "content": doc["content"]})
        return history

    async def get_all_sessions(self, user_id: str = None):
        match_stage = {}
        if user_id:
            match_stage = {"$match": {"user_id": user_id}}

        pipeline = []
        if match_stage:
            pipeline.append(match_stage)
        pipeline += [
            {"$group": {"_id": "$session_id", "last_msg": {"$last": "$content"}, "last_time": {"$last": "$timestamp"}}},
            {"$sort": {"last_time": -1}}
        ]

        cursor = self.messages.aggregate(pipeline)
        sessions_data = []
        async for doc in cursor:
            sessions_data.append({
                "sessionId": doc["_id"],
                "lastMessage": doc["last_msg"],
                "timestamp": doc["last_time"]
            })
        return sessions_data