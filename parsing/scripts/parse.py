import argparse
import json
import sys
import os

BASE_DIR = (os.path.abspath(os.path.dirname(__file__))).replace("/parsing/scripts", '')
sys.path.append(BASE_DIR)

from parsing.config import NODE_URL
from parsing.node import Node


def format_output(output):
    return {
        'index': output.index,
        'type': output.type,
        'type_name': output.type_name,
        'addresses': output.addresses,
        'script_hex': output.script_hex,
        'value': output.value,
        "value_denomination": output.value_denomination
    }


def format_input(input_data):
    return {
        'txid': input_data.txid,
        'txid_as_number': input_data.txid_as_number,
        'tx_hash': input_data.tx_hash,
        'tx_hash_as_number': input_data.tx_hash_as_number,
        'output_index': input_data.output_index,
        'script_sig': input_data.script_sig,
        'prev_output': format_output(input_data.prev_output)
    }


def format_transaction(tx):
    return {
        "id": tx.id,
        "id_as_number": tx.id_as_number,
        "hash": tx.id,
        "hash_as_number": tx.hash_as_number,
        "index": tx.index,
        "size": tx.size,
        "time": tx.time,
        "median_time": tx.median_time,
        "coinbase": tx.coinbase,
        "coinbase_script": tx.coinbase_script,
        "lock_time": tx.lock_time,
        "version": tx.version,
        "outputs": [format_output(output) for output in tx.get_outputs()],
        "inputs": [format_input(input_data) for input_data in tx.get_inputs()]
    }


def format_block(block):
    return {
        "hash": block.hash,
        "hash_as_number": block.hash_as_number,
        "chain_work_as_number": block.chain_work_as_number,
        "time": block.time,
        "median_time": block.median_time,
        "difficulty": block.difficulty,
        "height": block.height,
        "confirmations": block.confirmations,
        "merkle_root": block.merkle_root,
        "nonce": block.nonce,
        "next_block_hash_as_number": block.next_block_hash_as_number,
        "next_block_hash": block.next_block_hash,
        "prev_block_hash_as_number": block.prev_block_hash_as_number,
        "previous_block_hash": block.previous_block_hash,
        "size": block.size,
        "stripped_size": block.stripped_size,
        "version": block.version,
        "version_hex": block.version_hex,
        "weight": block.weight,
        'transactions': [format_transaction(tx) for tx in block.get_transactions()],
        'transaction_count': len(block.get_transactions())
    }


def main(block_heights):
    node = Node(NODE_URL)
    results = [format_block(node.get_block(height)) for height in block_heights]
    sys.stdout.write(json.dumps(results))


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--heights", nargs='+', default=None, help="List of block heights to parse.")
    args = argParser.parse_args()
    if not args.heights:
        raise Exception("No block heights provided.")

    block_heights = [int(height) for height in args.heights if height]
    main(block_heights)
