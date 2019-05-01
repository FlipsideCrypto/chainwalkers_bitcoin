from parsing.utils.jsonrpc import JsonRpcCaller
from parsing.schema import BlockSchema, TransactionSchema, OutputSchema
from datetime import datetime


class Node(object):

    SUPPORTS_GET_BLOCK_2 = True
    SHOULD_SAVE_COINBASE_SCRIPT = True

    def __init__(self, url, user=None, password=None):
        self.rpc_caller = JsonRpcCaller(url, user=user, password=password, tls=True)

    def get_block_count(self):
        return self.rpc_caller.call("getblockcount")

    def get_block(self, height):
        blockHash = self.rpc_caller.call("getblockhash", [height])
        if self.SUPPORTS_GET_BLOCK_2:
            block_dict = self.rpc_caller.call("getblock", [blockHash, 2])
        else:
            block_dict = self.rpc_caller.call("getblock", [blockHash])

        block = self.init_block(block_dict)
        tx_dicts = self.get_block_transactions(block_dict, block)

        tx_index = 0
        for tx_dict in tx_dicts:
            transaction = self.process_transaction(tx_dict, tx_index, block)
            block.add_transaction(transaction)
            tx_index += 1
        
        return block

    def get_block_transactions(self, block_dict, block_data):
        if self.SUPPORTS_GET_BLOCK_2:
            tx_dicts = block_dict["tx"]
            result = []
            for tx in tx_dicts:
                if not self.exclude_transaction(tx["txid"], block_data):
                    result.append(tx)
            return result
        else:
            hashes = []
            for tx_hash in block_dict["tx"]:
                if not self.exclude_transaction(tx_hash, block_data):
                    hashes.append(tx_hash)
            if len(hashes) > 0:
                return self.rpc_caller.bulkCall(("getrawtransaction", [tx_hash, 1]) for tx_hash in hashes)
            else:
                return []

    def init_block(self, block_dict):
        return BlockSchema(block_dict)

    def process_transaction(self, tx_dict, tx_index, block):
        transaction = self.init_transaction(tx_dict, tx_index, block)

        vin = tx_dict['vin']
        vout = tx_dict['vout']

        transaction = self.process_inputs(transaction, vin)
        transaction = self.process_outputs(transaction, vout)

        if transaction.transaction_is_coinbase(vin) and self.SHOULD_SAVE_COINBASE_SCRIPT:
            assert len(vin) == 1
            transaction.set_coinbase_script(vin[0]["coinbase"])

        return transaction

    def init_transaction(self, tx_dict, tx_index, block):
        return TransactionSchema(
            tx_dict,
            tx_index,
            block.time,
            block.median_time
        )

    def exclude_transaction(self, txHash, blockData):
        return False

    def process_inputs(self, transaction, vin):
        if transaction.coinbase:
            return transaction

        # Retrieve the inputs previous output value.
        inputs_prev_output_map = {}
        bulk_call_params = []
        for i, input_dict in enumerate(vin):
            txid = input_dict['txid']
            vout_index = input_dict['vout']
            inputs_prev_output_map["{}-{}".format(txid, vout_index)] = None
            bulk_call_params.append(("getrawtransaction", [txid, 1]))

        # Do this as a bulk RPC call to limit network requests.
        results = self.rpc_caller.bulk_call(bulk_call_params)

        for prev_tx in results:
            txid = prev_tx['txid']
            for vout in prev_tx['vout']:
                vout_index = vout['n']
                try:
                    inputs_prev_output_map["{}-{}".format(txid, vout_index)] = OutputSchema(vout, vout_index)
                except KeyError:
                    pass

        for input_index, input_dict in enumerate(vin):
            # Attach the inputs previous output value and addresses to the input.
            txid = input_dict['txid']
            vout_index = input_dict['vout']
            inputs_prev_output = inputs_prev_output_map["{}-{}".format(txid, vout_index)]
            transaction.add_input(input_dict, inputs_prev_output)

        return transaction

    def process_outputs(self, transaction, vout):
        for output_index, output_dict in enumerate(vout):
            transaction.add_output(output_dict, output_index)
        return transaction
