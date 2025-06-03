import redis
import json
from models import UserResponse
from typing import Optional

redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_user_from_cache(user_id: int) -> Optional[UserResponse]:
    user_data = redis_client.get(f"user:{user_id}")
    if user_data:
        return UserResponse(**json.loads(user_data))
    return None

def set_user_to_cache(user: UserResponse):
    redis_client.set(f"user:{user.id}", user.json())

def delete_user_from_cache(user_id: int):
    redis_client.delete(f"user:{user_id}")
