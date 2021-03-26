import os

import redis

r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=os.environ["REDIS_PORT"],
    password=os.environ["REDIS_PASSWORD"],
    ssl=True,
    decode_responses=True
)

def r_keys(pattern):
    return r.keys(pattern)

def h_set(name, key=None, value=None, mapping=None):
    return r.hset(name, key=key, value=value, mapping=mapping)

def s_set(name, value):
    return r.set(name, value)

def h_get(key, field):
    return r.hget(key, field)

def r_get_keys(key):
    return r.hkeys(key)

def r_del_keys(name, *keys):
    return r.hdel(name, *keys)

def get_stream(stream, field):
    return h_get(stream.user.login, field)

def set_stream(stream, field, value):
    return h_set(stream.user.login, field, value)
