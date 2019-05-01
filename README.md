# Chainwalkers Bitcoin Parser

This parser communicates with a Bitcoin node to extract and decodes blocks & transactions.

Chainwalkers Framework Docs: [docs.flipsidecrypto.com](https://docs.flipsidecrypto.com)

## Getting Started

Create a `.secrets.json` at the top level directory with a node url. Chainwalkers will use this to communicate with a Bitcoin node's RPC interface.

```json
{
  "NODE_URL": "{protocol}://{username}:{password}@{host}:{port}"
}
```

## Building

A docker image of the ethereum parser can be built by running:

```shell
bash builder_docker_image.sh
```

This will create an image with the tag `chainwalkers_ethereum:latest`.

## Up and Running

This parser has two entry points, each of which writes a json response to stdout.

1. `get_height.sh`: returns the current height
2. `parse_blocks.sh [int, int, ...]`: returns an array of decoded blocks and each blocks transactions

To get the latest height of the blockchain run:

```shell
> docker run chainwalkers_bitcoin:latest bash get_height.sh
{
    "height": 574158
}
```

To parse a list of blocks run:

```shell
> docker run chainwalkers_bitcoin:latest bash parse_blocks.sh 200000 200001 200002
[
    {
        "height": 200000,
        "hash": "000000000000034a7dedef4a161fa058a2d67a173a90155f3a2fe6fc132e0ebf",
        ...,
        "transactions": [
            {
                "id": "",
                "hash": "",
                "vin": [
                    {
                        "prev_output": {...},
                        ...
                    },
                    ...
                ],
                "vout": [...],
                ...
            }
        ],
        ...
    },
    ...
]
```

**Note that each "vin" object include a reference to it's previous output vector. This is required for all UTXO style chains integrating with Chainwalkers (we use bulk RPC calls to make the inclusion of this data as efficient as possible).**
