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
        'addresses': output.addresses,
        'index': output.index,
        'script_hex': output.script_hex,
        'type': output.type,
        'type_id': output.type_id,
        'value': output.value,
        "value_denomination": output.value_denomination
    }


def format_input(input_data):
    return {
        'output_index': input_data.output_index,
        'prev_output': format_output(input_data.prev_output),
        'script_sig': input_data.script_sig,
        'txid': input_data.txid,
        'txid_as_number': input_data.txid_as_number,
        "txinwitness": input_data.txinwitness
    }


def format_transaction(tx):
    return {
        "coinbase": tx.coinbase,
        "coinbase_script": tx.coinbase_script,
        "hash": tx.hash,
        "hash_as_number": tx.hash_as_number,
        "id": tx.id,
        "id_as_number": tx.id_as_number,
        "index": tx.index,
        "inputs": [format_input(input_data) for input_data in tx.get_inputs()],
        "lock_time": tx.lock_time,
        "median_time": tx.median_time,
        "outputs": [format_output(output) for output in tx.get_outputs()],
        "size": tx.size,
        "time": tx.time,
        "version": tx.version,
        "vsize": tx.vsize
    }


def format_block(block):
    return {
        "bits": block.bits,
        "chain_work": block.chain_work,
        "chain_work_as_number": block.chain_work_as_number,
        "confirmations": block.confirmations,
        "difficulty": block.difficulty,
        "height": block.height,
        "hash": block.hash,
        "hash_as_number": block.hash_as_number,
        "median_time": block.median_time,
        "merkle_root": block.merkle_root,
        "next_block_hash": block.next_block_hash,
        "next_block_hash_as_number": block.next_block_hash_as_number,
        "nonce": block.nonce,
        "prev_block_hash": block.previous_block_hash,
        "prev_block_hash_as_number": block.previous_block_hash_as_number,
        "size": block.size,
        "stripped_size": block.stripped_size,
        "time": block.time,
        'transactions': [format_transaction(tx) for tx in block.get_transactions()],
        'transaction_count': len(block.get_transactions()),
        "version": block.version,
        "version_hex": block.version_hex,
        "weight": block.weight
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
