import logging
import uuid
from bip32 import BIP32

from src.bitcoin.musig import generate_musig_key
from src.bitcoin.address import program_to_witness
from src.bitcoin.key import ECPubKey
from src.bitcoin.messages import sha256
from src.coordinator.mempool_space_client import get_transaction

COMMANDS = ['address', 'spend', 'wallet', 'xpub']

# temporarily keep signer xpubs in memory
signer_xpubs = []

def is_valid_command(command: str):
    return command in COMMANDS

def create_wallet(payload: dict):
    if (not 'quorum' in payload):
        raise Exception("[wallet] Cannot create a wallet without the 'quorum' property")

    quorum = payload['quorum']
    if (quorum < 1):
        raise Exception("[wallet] Quorum must be greater than 1")

    new_wallet_id = str(uuid.uuid4())

    # TODO add to a database
    return new_wallet_id

def get_wallet_id(payload: dict):
    if (not 'wallet_id' in payload):
        raise Exception("[wallet] Cannot add an xpub without the 'wallet_id' property")

    wallet_id = payload['wallet_id']
    return wallet_id

def add_xpub(payload: dict):
    if (not 'xpub' in payload):
        raise Exception("[wallet] Cannot add an xpub without the 'xpub' property")

    xpub = payload['xpub']
    wallet_id = get_wallet_id(payload)

    # add xpub to the end of the in memory list of xpubs
    signer_xpubs.append(xpub)
    logging.info('[wallet] Added xpub to wallet %s', wallet_id)

def get_address(payload: dict):
    # TODO get address at a specific index. For now hardcode this to 0
    # index = payload['index']
    index = 0
    wallet_id = get_wallet_id(payload)
    ec_public_keys = []

    if (signer_xpubs == []):
        raise Exception('[wallet] No xpubs to create an address from!')

    for xpub in signer_xpubs:
        logging.info(xpub)
        bip32_node = BIP32.from_xpub(xpub)
        public_key = bip32_node.get_pubkey_from_path(f"m/{index}")

        # The method to generate and aggregate MuSig key expects ECPubKey objects
        ec_public_key = ECPubKey()
        ec_public_key.set(public_key)
        ec_public_keys.append(ec_public_key)

    c_map, pubkey_agg = generate_musig_key(ec_public_keys)
    logging.info('[wallet] Aggregate public key: %s', pubkey_agg.get_bytes().hex())

    # Create a segwit v1 address (P2TR) from the aggregate key
    p2tr_address = program_to_witness(0x01, pubkey_agg.get_bytes())
    logging.info('[wallet] Returning P2TR address %s', p2tr_address)

    # convert the challenges/coefficients to hex so they can be returned to the signer
    c_map_hex = {}
    for key, value in c_map.items():
        k = key.get_bytes().hex()
        c_map_hex[k] = value.hex()

    return [p2tr_address, c_map_hex, pubkey_agg.get_bytes().hex()]

def start_spend(payload: dict):
    # create an ID for this request
    spend_request_id = str(uuid.uuid4())

    if (not 'txid' in payload):
        raise Exception("[wallet] Cannot spend without the 'txid' property, which corresponds to the transaction ID of the output that is being spent")

    if (not 'output_index' in payload):
        raise Exception("[wallet] Cannot spend without the 'output_index' property, which corresponds to the index of the oputput that is being spent")

    if (not 'new_address' in payload):
        raise Exception("[wallet] Cannot spend without the 'new_address' property, which corresponds to the destination address of the transaction")

    txid = payload['txid']
    output_index = payload['output_index']
    destination_address = payload['new_address']

    # Use mempool.space to look up the scriptpubkey for the output being spent
    # Can probably find a library to do this so we don't have to make any external calls
    tx = get_transaction(txid)
    script_pub_key = tx['vout'][output_index]['scriptpubkey']

    # TODO package up the txid, output_index, script_pub_key, and destination_address up
    # and persist, or somehow make available to signers
    # For now, just return the request ID
    return spend_request_id



