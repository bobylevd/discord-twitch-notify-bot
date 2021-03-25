import os

import redis

r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=os.environ["REDIS_PORT"],
    password=os.environ["REDIS_PASSWORD"],
    ssl=True,
    decode_responses=True
)

def all_keys():
    return r.keys("*")

def r_set(key, field, value):
    return r.hset(key.lower(), field.lower(), value.lower())

def r_get(key, field):
    return r.hget(key.lower(), field.lower())

def r_get_keys(key):
    return r.hkeys(key.lower())

def r_del_keys(name, *keys):
    return r.hdel(name.lower(), *keys)

def get_stream(stream, field):
    return r_get(stream.user.login, field)

def set_stream(stream, field, value):
    return r_set(stream.user.login, field, value)
