# Created: dylannguyen
import json
from typing import List
from aioredis import Redis
from app.database.models.message import Messages

# class RecentChatCache(AbstractCache):
#     pass
    
async def serialize_message(message: Messages):
    return {
        "session_id": message.session_id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at.isoformat()
    }

async def save_message_to_cache(session_id: str, messages: List[dict], redis_client: Redis):
    cache_key = f"chat:thread:{session_id}"
    await redis_client.lpush(
        cache_key=cache_key,
        value=json.dumps(messages, default=str)
    )
    await redis_client.ltrim(cache_key, 0, 99)

async def get_message_from_cache(session_id: str, redis_client: Redis):
    cache_key = f"chat:thread:{session_id}"
    cached_data = await redis_client.lrange(name= cache_key, start=0, end=99)
    return [json.loads(msg) for msg in cached_data]