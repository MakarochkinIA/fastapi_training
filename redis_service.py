import json
import redis

from redis import asyncio as aioredis
from redis.asyncio.client import Redis
from config import settings


async def redis_client():
    try:
        return await aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            encoding="utf8", decode_responses=True
        )
    except redis.exceptions.ConnectionError as e:
        print("Connection error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)


async def listen_to_channel(user_id: str, redis_conn: Redis):
    async with redis_conn.pubsub() as listener:
        await listener.subscribe(settings.PUSH_NOTIFICATIONS_CHANNEL)
        while True:
            message = await listener.get_message()
            if message is None:
                continue
            if message.get("type") == "message":
                msg = json.loads(message["data"])
                if user_id not in msg.get('recievers'):
                    continue
                yield {"data": msg}
