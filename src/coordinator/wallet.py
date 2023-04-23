import logging
import uuid
from bip32 import BIP32

from src.bitcoin.musig import generate_musig_key, aggregate_schnorr_nonces, aggregate_musig_signatures
from src.bitcoin.address import program_to_witness
from src.bitcoin.key import ECPubKey
from src.bitcoin.messages import CTransaction, CTxIn, COutPoint, CTxOut, CScriptWitness, CTxInWitness
from src.bitcoin.script import TaprootSignatureHash, SIGHASH_ALL_TAPROOT
from src.coordinator.mempool_space_client import broadcast_transaction, get_transaction

# Using Peter Todd's python-bitcoinlib (https://github.com/petertodd/python-bitcoinlib)
from bitcoin.wallet import CBitcoinAddress
import bitcoin

# can abstract this network selection bit out to a properties/config file
bitcoin.SelectParams('testnet')

COMMANDS = ['address', 'nonce','spend', 'wallet', 'xpub']

# in memory cache of transactions that are in the process of being spent
# keys are aggregate nonces and values are spending transactions
spending_txs = {}

def is_valid_command(command: str):
    return command in COMMANDS

def create_spending_transaction(txid, outputIndex, destination_addr, amount_sat, version=1, nSequence=0):
    """Construct a CTransaction object that spends the first ouput from txid."""
    # Construct transaction
    spending_tx = CTransaction()
    # Populate the transaction version
    spending_tx.nVersion = version
    # Populate the locktime
    spending_tx.nLockTime = 0

    # Populate the transaction inputs
    outpoint = COutPoint(int(txid, 16), outputIndex)
    spending_tx_in = CTxIn(outpoint=outpoint, nSequence=nSequence)
    spending_tx.vin = [spending_tx_in]

    script_pubkey = CBitcoinAddress(destination_addr).to_scriptPubKey()
    dest_output = CTxOut(nValue=amount_sat, scriptPubKey=script_pubkey)
    spending_tx.vout = [dest_output]

    return (spending_tx, script_pubkey)


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

# Get a wallet ID from the provided payload. Throw an error if it is missing.
def get_wallet_id(payload: dict):
    if (not 'wallet_id' in payload):
        raise Exception("[wallet] 'wallet_id' property is missing")

    wallet_id = payload['wallet_id']
    return wallet_id

# Get the spend request ID from the provided payload. Throw an error if it is missing
def get_spend_request_id(payload: dict):
    if (not 'spend_request_id' in payload):
        raise Exception("[wallet] 'spend_request_id' property is missing")

    spend_request_id = payload['spend_request_id']
    return spend_request_id

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
        # The method to generate and aggregate MuSig key expects ECPubKey objects
        ec_public_key = ECPubKey()

        # TODO xpubs aren't working quite right. Using regular public keys for now.
        # bip32_node = BIP32.from_xpub(xpub['xpub'])
        # public_key = bip32_node.get_pubkey_from_path(f"m/{index}")
        #e c_public_key.set(public_key)

        ec_public_key.set(bytes.fromhex(xpub['xpub']))
        ec_public_keys.append(ec_public_key)

    c_map, pubkey_agg = generate_musig_key(ec_public_keys)
    logging.info('[wallet] Aggregate public key: %s', pubkey_agg.get_bytes().hex())

    # Create a segwit v1 address (P2TR) from the aggregate key
    p2tr_address = program_to_witness(0x01, pubkey_agg.get_bytes())
    logging.info('[wallet] Returning P2TR address %s', p2tr_address)

    # convert the challenges/coefficients to hex so they can be returned to the signer
    c_map_hex = {}
    for key, value in c_map.items():
        # k is the hex encoded pubkey, the value is the challenge/coefficient
        k = key.get_bytes().hex()
        c_map_hex[k] = value.hex()

    return [p2tr_address, c_map_hex, pubkey_agg.get_bytes().hex()]

# Initiates a spending transaction
def start_spend(payload: dict, db):
    # create an ID for this request
    spend_request_id = str(uuid.uuid4())
    logging.info('[wallet] Starting spend request with id %s', spend_request_id)


    if (not 'txid' in payload):
        raise Exception("[wallet] Cannot spend without the 'txid' property, which corresponds to the transaction ID of the output that is being spent")

    if (not 'output_index' in payload):
        raise Exception("[wallet] Cannot spend without the 'output_index' property, which corresponds to the index of the oputput that is being spent")

    if (not 'new_address' in payload):
        raise Exception("[wallet] Cannot spend without the 'new_address' property, which corresponds to the destination address of the transaction")

    if (not 'value' in payload):
        raise Exception("[wallet] Cannot spend without the 'value' property, which corresponds to the value (in satoshis) of the output that is being spent")

    txid = payload['txid']
    output_index = payload['output_index']
    destination_address = payload['new_address']
    wallet_id = get_wallet_id(payload)

    # 10% of fees will go to miners. Can have better fee support in the future
    output_amount = int(payload['value'] * 0.9)

    # Use mempool.space to look up the scriptpubkey for the output being spent
    # Could probably find a library to do this so we don't have to make any external calls
    tx = get_transaction(txid)
    input_script_pub_key = tx['vout'][output_index]['scriptpubkey']
    input_value_sats = tx['vout'][output_index]['value']

    # Persist to the db so other signers can easily retrieve this information
    if (db.add_spend_request(txid,
                             output_index,
                             input_script_pub_key,
                             input_value_sats,
                             spend_request_id,
                             destination_address,
                             output_amount,
                             wallet_id)):
        logging.info('[wallet] Saved spend request %s to the database', spend_request_id)

    return spend_request_id

def save_nonce(payload: dict, db):
    if (not 'nonce' in payload):
        raise Exception("[wallet] Cannot save a nonce without the 'nonce' property")

    nonce = payload['nonce']
    spend_request_id = get_spend_request_id(payload)
    spend_request = db.get_spend_request(spend_request_id)
    wallet_id = spend_request['wallet_id']
    print(wallet_id)

    logging.info('[wallet] Saving nonce for request id %s', spend_request_id)

    wallet = db.get_wallet(wallet_id)

    # Save the nonce to the db
    db.add_nonce(nonce, spend_request_id)

    logging.info('[wallet] Successfully saved nonce for request id %s', spend_request_id)

    # When the last signer provides a nonce, we can return the aggregate nonce (R_AGG)
    nonces = db.get_all_nonces(spend_request_id)

    if (len(nonces) != wallet['quorum']):
        return None

    # Generate nonce points
    nonce_points = [ECPubKey().set(bytes.fromhex(nonce['nonce'])) for nonce in nonces]
    # R_agg is the aggregate nonce, negated is if the private key was negated to produce
    # an even y coordinate
    R_agg, negated = aggregate_schnorr_nonces(nonce_points)

    (spending_tx, _script_pub_key) = create_spending_transaction(spend_request['txid'],
        spend_request['output_index'],
        spend_request['new_address'],
        spend_request['value'])

    # Create a sighash for ALL (0x00)
    sighash_musig = TaprootSignatureHash(spending_tx, [{'n': spend_request['output_index'], 'nValue': spend_request['prev_value_sats'], 'scriptPubKey': bytes.fromhex(spend_request['prev_script_pubkey'])}], SIGHASH_ALL_TAPROOT)
    print(sighash_musig)

    # Update cache
    spending_txs[R_agg] = spending_tx

    # Encode everything as hex before returning
    return (R_agg.get_bytes().hex(), sighash_musig.hex(), negated)

def save_signature(payload, db):
    if (not 'signature' in payload):
        raise Exception("[wallet] Cannot save a signature without the 'signature' property")

    signature = payload['signature']
    spend_request_id = get_spend_request_id(payload)

    logging.info("[wallet] Recieved partial signature for spend request %s", spend_request_id)

    db.add_partial_signature(signature, spend_request_id)

    spend_request = db.get_spend_request(spend_request_id)
    wallet_id = spend_request['wallet_id']
    wallet = db.get_wallet(wallet_id)

    sigs = db.get_all_signatures(spend_request_id)
    sigs = [sig['signature'] for sig in sigs]

    nonces = db.get_all_nonces(spend_request_id)
    quorum = wallet['quorum']
    if len(nonces) != quorum or len(sigs) != quorum:
        logging.error('[wallet] Number of nonces and signatures does not match expected quorum of %d', quorum)
        return None

    nonce_points = [ECPubKey().set(bytes.fromhex(nonce['nonce'])) for nonce in nonces]

    # Aggregate keys and signatures
    R_agg, negated = aggregate_schnorr_nonces(nonce_points)

    # Retrieve the current transaction from the cache
    spending_tx = spending_txs[R_agg]

    # The aggregate signature
    tx_sig_agg = aggregate_musig_signatures(sigs, R_agg)

    # Add the aggregate signature to the witness stack
    witness_stack = CScriptWitness()
    witness_stack.stack.append(tx_sig_agg)

    # Add the witness to the transaction
    spending_tx.wit.vtxinwit.append(CTxInWitness(witness_stack))

    tx_serialized_hex = spending_tx.serialize().hex()
    logging.info("[wallet] Serialized transaction hex, ready for broadcast: %s", tx_serialized_hex)

    # Uncomment to broadcast tx
    # txid = broadcast_transaction(raw_tx)
    # print("TXID", txid)

    return tx_serialized_hex


