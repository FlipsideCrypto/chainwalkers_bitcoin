from datetime import datetime
import time

HASH_PRECISION = 78
CHAINWORK_PRECISION = 48
OUTPUT_VALUE_PRECISION = 32
MAX_ADDRESS_LENGTH = 90
OUTPUT_TYPES = {
    "nulldata": 0,
    "nonstandard": 1,
    "pubkeyhash": 2,
    "pubkey": 3,
    "multisig": 4,
    "scripthash": 5,
    "witness_v0_keyhash": 6,
    "witness_v0_scripthash": 7,
    "stakegen": 64,
    "stakesubmission": 65,
    "sstxcommitment": 66,
    "sstxchange": 67,
    "stakerevoke": 68,
    "pubkeyalt": 69,
}


class BlockSchema(object):

    def __init__(self, data):
        self.hash = data['hash']
        self.hash_as_number = int(data["hash"], base=16)
        assert(self.hash_as_number < 10**HASH_PRECISION)

        self.previous_block_hash_as_number = None
        self.previous_block_hash = None
        if data.get("previousblockhash"):
            self.previous_block_hash_as_number = int(data["previousblockhash"], base=16)
            self.previous_block_hash = data['previousblockhash']
            assert(self.previous_block_hash_as_number < 10**HASH_PRECISION)

        self.next_block_hash = None
        self.next_block_hash_as_number = None
        if data.get("nextblockhash"):
            self.next_block_hash = data["nextblockhash"]
            self.next_block_hash_as_number = int(data["nextblockhash"], base=16)
            assert(self.next_block_hash_as_number < 10**HASH_PRECISION)

        self.chain_work = data["chainwork"]
        self.chain_work_as_number = self.get_block_chainwork(data)
        assert(self.chain_work_as_number < 10**CHAINWORK_PRECISION)

        self.time = datetime.strftime(
            datetime.utcfromtimestamp(data["time"]),
            "%Y-%m-%dT%H:%M:%S"
        )
        self.median_time = datetime.strftime(
            self.get_block_median_time(data), 
            "%Y-%m-%dT%H:%M:%S"
        )
        self.difficulty = float(data["difficulty"])
        self.height = int(data["height"])
        self.confirmations = data['confirmations']
        self.merkle_root = data['merkleroot']
        self.nonce = data['nonce']
        self.size = int(data['size'])
        self.bits = int(data['bits'], 16)
        self.stripped_size = data['strippedsize']
        self.version = data['version']
        self.version_hex = data['versionHex']
        self.weight = data['weight']
        self.transactions = []                

    def get_block_chainwork(self, block_dict):
        return int(block_dict["chainwork"], base=16)

    def get_block_median_time(self, block_dict):
        return datetime.utcfromtimestamp(block_dict["mediantime"])

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def get_transactions(self):
        return self.transactions


class OutputSchema(object):

    def __init__(self, data, output_index):
        if not data["scriptPubKey"]["type"] in OUTPUT_TYPES:
            print(data["scriptPubKey"]["type"])
        assert(data["scriptPubKey"]["type"] in OUTPUT_TYPES)

        if "addresses" in data["scriptPubKey"]:
            addresses = data["scriptPubKey"]["addresses"]           
        else:
            addresses = []

        output_type = OUTPUT_TYPES[data["scriptPubKey"]["type"]]

        if output_type in [OUTPUT_TYPES["nonstandard"], OUTPUT_TYPES["nulldata"], OUTPUT_TYPES["multisig"]]:
            pass
        elif output_type == OUTPUT_TYPES["pubkey"]:
            if "addresses" in data["scriptPubKey"]:
                assert(len(addresses) == 1)
        elif output_type in [OUTPUT_TYPES["witness_v0_keyhash"], OUTPUT_TYPES["witness_v0_scripthash"]]:
            self.process_segwit_output(addresses)
        else:
            assert len(addresses) == 1

        for address in addresses:
            assert(len(address) <= MAX_ADDRESS_LENGTH)
            assert(len(address) > 0)

        script_hex = data["scriptPubKey"]["hex"]
        value = self.output_value_to_satoshis(data["value"])
        self.index = output_index
        self.type = data["scriptPubKey"]["type"]
        self.type_id = output_type
        self.addresses = addresses
        self.script_hex = script_hex
        self.value = value
        self.value_denomination = "satoshis"

    def process_segwit_output(self, addresses):
        assert len(addresses) == 1
    
    def output_value_to_satoshis(self, output_value):
        if type(output_value) != int:
            assert(float(output_value) >= 0.0)

            value_pieces = output_value.split(".")
            assert(len(value_pieces) == 2)

            fraction_digit_count = len(value_pieces[1])
            digits = int("".join(value_pieces))
            value = digits * 10**(8 - fraction_digit_count)
            naiveValue = float(output_value) * 100000000.0
            assert(abs(value - naiveValue) <= 1024)
        else:
            value = output_value * 100000000

        assert(value < 10**OUTPUT_VALUE_PRECISION)
        assert(value >= 0)

        return value


class InputSchema(object):

    def __init__(self, data):
        input_tx_id_as_number = int(data["txid"], base=16)
        assert(input_tx_id_as_number < 10**HASH_PRECISION)

        self.txid = data["txid"]
        self.txid_as_number = input_tx_id_as_number
        self.output_index = int(data["vout"])
        self.script_sig = data["scriptSig"]["hex"]
        self.txinwitness = data.get("txinwitness")
        self.prev_output = None

    def set_prev_output(self, output):
        self.prev_output = output

    def get_prev_output(self):
        return self.prev_output


class TransactionSchema(object):

    def __init__(self, data, tx_index, tx_time, tx_median_time):
        tx_id_as_number = int(data["txid"], base=16)
        assert(tx_id_as_number < 10**HASH_PRECISION)

        tx_hash_as_number = int(data["hash"], base=16)
        assert(tx_hash_as_number < 10**HASH_PRECISION)

        self.id = data['txid']
        self.id_as_number = tx_id_as_number
        self.hash = data['hash']
        self.hash_as_number = tx_hash_as_number
        self.index = tx_index
        self.size = int(data['size'])
        self.vsize = int(data['vsize'])
        self.time = tx_time
        self.median_time = tx_median_time
        self.coinbase = self.transaction_is_coinbase(data['vin'])
        self.coinbase_script = None
        self.lock_time = data['locktime']
        self.version = data['version']
        self.inputs = []
        self.outputs = []

    def transaction_is_coinbase(self, vin):
        for input_dict in vin:
            if "coinbase" in input_dict:
                return True
        return False

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

    def add_input(self, input_dict, prev_output):
        input_data = InputSchema(input_dict) 
        input_data.set_prev_output(prev_output)
        self.inputs.append(input_data)

    def add_output(self, output_dict, output_index):
        self.outputs.append(OutputSchema(output_dict, output_index))

    def set_coinbase_script(self, coinbase_script):
        self.coinbase_script = coinbase_script

    def get_coinbase_script(self):
        return self.coinbase_script

    def get_hash_string(self):
        result = hex(self.tx_hash)[2:]
        while len(result) < 64:
            result = "0" + result
        return result
