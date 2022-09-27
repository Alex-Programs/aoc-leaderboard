import json


def get_config():
    with open("config.json") as r:
        return json.loads(r.read())
