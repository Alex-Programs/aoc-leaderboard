import json

class Cache:
    data = {}

def get_config():
    if Cache.data:
        return Cache.data

    with open("config.json") as r:
        Cache.data = json.loads(r.read())
        return Cache.data