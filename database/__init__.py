import os

import redis

r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=os.environ["REDIS_PORT"],
    db=os.environ["REDIS_DB"],
    decode_responses=True
)
