import logging
import uuid
from bip32 import BIP32

from src.bitcoin.musig import generate_musig_key
from src.bitcoin.address import program_to_witness
from src.bitcoin.key import ECPubKey
from src.bitcoin.messages import sha256
from src.coordinator.mempool_space_client import get_transaction

COMMANDS = ['address', 'spend', 'wallet', 'xpub']

def is_valid_command(command: str):
    return command in COMMANDS

def create_wallet(payload: dict, db):
    if (not 'quorum' in payload):
        raise Exception("[wallet] Cannot create a wallet without the 'quorum' property")

    quorum = payload['quorum']
    if (quorum < 1):
        raise Exception("[wallet] Quorum must be greater than 1")

    new_wallet_id = str(uuid.uuid4())

    if (db.add_wallet(new_wallet_id, quorum)):
        logging.info("[wallet] Saved new wallet ID %s to the database", new_wallet_id)
    return new_wallet_id

# Get a wallet ID from the provided payload. Throw an error if it is missing
def get_wallet_id(payload: dict):
    if (not 'wallet_id' in payload):
        raise Exception("[wallet] Cannot add an xpub without the 'wallet_id' property")

    wallet_id = payload['wallet_id']
    return wallet_id

def add_xpub(payload: dict, db):
    if (not 'xpub' in payload):
        raise Exception("[wallet] Cannot add an xpub without the 'xpub' property")

    xpub = payload['xpub']
    wallet_id = get_wallet_id(payload)

    if (db.add_xpub(wallet_id, xpub)):
        logging.info('[wallet] Added xpub to wallet %s', wallet_id)

def get_address(payload: dict, db):
    index = payload['index']
    wallet_id = get_wallet_id(payload)
    ec_public_keys = []

    # wallet = db.get_wallet(wallet_id)
    wallet_xpubs = db.get_xpubs(wallet_id)

    if (wallet_xpubs == []):
        raise Exception('[wallet] No xpubs to create an address from!')

    for xpub in wallet_xpubs:
        bip32_node = BIP32.from_xpub(xpub['xpub'])
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

# Initiates a spending transaction
def start_spend(payload: dict, db):
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
    # Could probably find a library to do this so we don't have to make any external calls
    tx = get_transaction(txid)
    script_pub_key = tx['vout'][output_index]['scriptpubkey']

    # Persist to the db so other signers can easily retrieve this information
    if (db.add_spend_request(txid,
                             output_index,
                             script_pub_key,
                             spend_request_id,
                             destination_address)):
        logging.info('[wallet] Saved spend request %s to the database', spend_request_id)

    return spend_request_id

def save_nonce(payload: dict, db):
    if (not 'nonce' in payload):
        raise Exception("[wallet] Cannot save a nonce without the 'nonce' property")
    if (not 'spend_request_id' in payload):
        raise Exception("[wallet] Cannot save a nonce without the 'spend_request_id' property")

    nonce = payload['nonce']
    spend_request_id = payload['spend_request_id']



