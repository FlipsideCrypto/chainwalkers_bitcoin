import json
import sys
import os

BASE_DIR = (os.path.abspath(os.path.dirname(__file__))).replace("/parsing/scripts", '')
sys.path.append(BASE_DIR)

from parsing.node import Node
from parsing.config import NODE_HOST, NODE_AUTH_PARAM, NODE_PORT


def main():
    node = Node(NODE_HOST, NODE_PORT, NODE_AUTH_PARAM)
    height = node.get_block_count()
    data = json.dumps({"height": height})
    sys.stdout.write(data)


if __name__ == "__main__":
    main()
