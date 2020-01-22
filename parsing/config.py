import json

def get_secrets():
    with open("/chainwalkers_parser/.secrets.json", "r") as f:
        return json.loads(f.read())

secrets = get_secrets()

NODE_HOST = secrets['NODE_HOST']
NODE_PORT = secrets['NODE_PORT']
NODE_AUTH_PARAM = secrets['NODE_AUTH_PARAM']
