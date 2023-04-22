import logging
import uuid

from src.bitcoin.musig import generate_musig_key
from src.bitcoin.address import program_to_witness
from src.bitcoin.key import generate_bip340_key_pair
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

# May have to simplify this and end up just taking a public key instead of an xpub
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

    # TODO BIP32 - derive public key from xpub
    # uncomment the following lines to show that this method works when plain pubkeys
    # are used
    # privkey1, pubkey1 = generate_bip340_key_pair(sha256(b'key0'))
    # c_map, pubkey_agg = generate_musig_key([pubkey1])

    c_map, pubkey_agg = generate_musig_key([signer_xpubs])
    logging.info('[wallet] Aggregate public key: %s', pubkey_agg.get_bytes().hex())

    # Create a segwit v1 address (P2TR) from the aggregate key
    p2tr_address = program_to_witness(0x01, pubkey_agg.get_bytes())
    logging.info('[wallet] Returning P2TR address %s', p2tr_address)

    # TODO also return the challenges/coefficients?
    return [p2tr_address]

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



