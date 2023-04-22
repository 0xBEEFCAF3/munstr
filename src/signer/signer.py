from nostr.filter import Filter, Filters
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from nostr.key import PrivateKey
from nostr.bech32 import encode, decode
from nostr.subscription import Subscription

from colorama import Fore

from src.signer.wallet import Wallet
from src.utils.nostr_utils import generate_nostr_message, add_relays, construct_and_publish_event, init_relay_manager, read_nsec
from src.utils.payload import is_valid_json, is_valid_payload

import json
import ssl
import time
import uuid
import logging

header = """
  ██████  ██▓  ▄████  ███▄    █ ▓█████  ██▀███  
▒██    ▒ ▓██▒ ██▒ ▀█▒ ██ ▀█   █ ▓█   ▀ ▓██ ▒ ██▒
░ ▓██▄   ▒██▒▒██░▄▄▄░▓██  ▀█ ██▒▒███   ▓██ ░▄█ ▒
  ▒   ██▒░██░░▓█  ██▓▓██▒  ▐▌██▒▒▓█  ▄ ▒██▀▀█▄  
▒██████▒▒░██░░▒▓███▀▒▒██░   ▓██░░▒████▒░██▓ ▒██▒
▒ ▒▓▒ ▒ ░░▓   ░▒   ▒ ░ ▒░   ▒ ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
░ ░▒  ░ ░ ▒ ░  ░   ░ ░ ░░   ░ ▒░ ░ ░  ░  ░▒ ░ ▒░
░  ░  ░   ▒ ░░ ░   ░    ░   ░ ░    ░     ░░   ░ 
      ░   ░        ░          ░    ░  ░   ░     
"""

CORDINATOR_TIMEOUT = 5  # seconds

def read_nsec():
    with open('src/signer/nsec.txt', 'r') as f:
        try:
            nsec = f.read()
            private_key = PrivateKey().from_nsec(nsec)
            return private_key
        except (error):
            print("Unexpected error reading nsec.txt")
            sys.exit(1)


def read_cordinator_pk():
    with open('src/signer/coordinator_pk.txt', 'r') as f:
        try:
            return f.read()
        except (error):
            print("Unexpected error reading nsec.txt")
            sys.exit(1)

def read_cordinator_messages(relay_manager, private_key, time_stamp_filter=None):
    payloads = []
    while relay_manager.message_pool.has_events():
        event_msg = relay_manager.message_pool.get_event()
        # Uncomment in debug
        # print(f"Message content: {event_msg.event.content}")
        # print(f"From Public key {event_msg.event.public_key}")
        if not is_valid_json(event_msg.event.content):
            continue

        json_payload = json.loads(event_msg.event.content)
        if not is_valid_payload(json_payload):
            continue

        if time_stamp_filter != None and json_payload['ts'] < time_stamp_filter:
            continue

        payloads.append(json_payload)
    return payloads


def handle_create_wallet(quorum, relay_manager, private_key):
    time_stamp = int(time.time())
    req_id = str(uuid.uuid4())
    new_wallet_payload = generate_nostr_message(
        command='wallet', req_id=req_id, payload={'quorum': quorum})
    construct_and_publish_event(new_wallet_payload, private_key, relay_manager)
    print('Nostr payload sent to cordinator, awaiting response')
    # Wait for a bit, ideally this is a expoentially backoff waiting period where we timeout after n tries
    time.sleep(CORDINATOR_TIMEOUT)
    payloads = read_cordinator_messages(
        relay_manager, private_key, time_stamp_filter=time_stamp)

    filtered_payloads = [payload for payload in payloads if payload['command']
                         == "wallet" and payload['ref_id'] == req_id]

    if len(filtered_payloads) == 0:
        print('Cordinator did not respond to create wallet command')
        return None
    my_wallet_create_payload = filtered_payloads[0]
    if my_wallet_create_payload == None:
        print('Cordinator did not respond to create wallet command')
        return None

    print(
        f"Wallet created with the following id {my_wallet_create_payload['payload']['wallet_id']}")

    return my_wallet_create_payload['payload']['wallet_id']

# NOTE creating an xpub does not expect a response


def handle_create_xpub(wallet, relay_manager, private_key):
    xpub = wallet.get_root_xpub()
    add_xpub_payload = generate_nostr_message(
        command='xpub', payload={'wallet_id': wallet.get_wallet_id(), 'xpub': wallet.get_pubkey()})
    construct_and_publish_event(add_xpub_payload, private_key, relay_manager)
    print("Operation Finished")


def handle_get_address(wallet, index, relay_manager, private_key):
    time_stamp = int(time.time())
    req_id = str(uuid.uuid4())
    get_address_paylaod = generate_nostr_message(command='address', req_id=req_id, payload={
                                                 'wallet_id': wallet.get_wallet_id(), 'index': index})
    construct_and_publish_event(
        get_address_paylaod, private_key, relay_manager)

    print('Nostr payload sent to cordinator, awaiting response')
    # Wait for a bit, ideally this is a expoentially backoff waiting period where we timeout after n tries
    time.sleep(CORDINATOR_TIMEOUT)
    payloads = read_cordinator_messages(
        relay_manager, private_key, time_stamp_filter=time_stamp)

    filtered_payloads = [payload for payload in payloads if payload['command']
                         == "address" and payload['ref_id'] == req_id]
    if len(filtered_payloads) == 0:
        print('Cordinator did not respond to get address command')
        return None
    # Server shouldnt respond with > 1 notes
    address_response = filtered_payloads[0]
    if address_response == None:
        print('Cordinator did not respond to get address command')
        return None

    return address_response['payload']


def handle_spend(outpoint, new_address, value, wallet, relay_manager, private_key):
    time_stamp = int(time.time())
    req_id = str(uuid.uuid4())
    start_spend_payload = generate_nostr_message(command='spend', req_id=req_id, payload={'wallet_id': wallet.get_wallet_id(
    ), 'txid': outpoint[0], 'output_index': outpoint[1], 'new_address': new_address, 'value': value})
    construct_and_publish_event(
        start_spend_payload, private_key, relay_manager)

    print('Nostr payload sent to cordinator, awaiting response')
    # Wait for a bit, ideally this is a expoentially backoff waiting period where we timeout after n tries
    time.sleep(CORDINATOR_TIMEOUT)
    payloads = read_cordinator_messages(
        relay_manager, private_key, time_stamp_filter=time_stamp)

    filtered_payloads = [payload for payload in payloads if payload['command']
                         == "spend" and payload['ref_id'] == req_id]
    if len(filtered_payloads) == 0:
        print('Cordinator did not respond to spend command')
        return None
    # Server shouldnt respond with > 1 notes
    spend_response = filtered_payloads[0]
    if spend_response == None:
        print('Cordinator did not respond to spend command')
        return None
    return spend_response['payload']['spend_request_id']


def handle_sign_tx(spend_request_id, wallet, relay_manager, private_key):
    time_stamp = int(time.time())
    req_id = str(uuid.uuid4())
    nonce = wallet.get_new_nonce().get_bytes().hex()
    nonce_payload = generate_nostr_message(command='nonce', req_id=req_id, payload={
                                                 'spend_request_id': spend_request_id, 'nonce': nonce})
    construct_and_publish_event(
        nonce_payload, private_key, relay_manager)

    print('Nonce Send! Awaiting response...')
    # Wait for a bit, ideally this is a expoentially backoff waiting period where we timeout after n tries
    time.sleep(CORDINATOR_TIMEOUT)
    # Here we want to wait for other signers to provide their nonces
    # Also assuming the cordinator will not send other types of messages
    nonce_response = None
    while 1:
        if not relay_manager.message_pool.has_events():
            print("Waiting for other signers to send nonce.. ")
            time.sleep(5)

        payloads = read_cordinator_messages(
            relay_manager, private_key, time_stamp_filter=time_stamp)
        filtered_payloads = [payload for payload in payloads if payload['command']
                            == "nonce" and payload['payload']['spend_request_id'] == spend_request_id]
        print(filtered_payloads)
        if len(filtered_payloads) == 0:
            print('Cordinator did not respond to spend command')
            continue
        # Server shouldnt respond with > 1 nonce notes
        nonce_response = filtered_payloads[0]
        break
    if nonce_response == None:
        print('Cordinator did not respond to nonce command ')
        return None
    # At this point all signers provided nonces so we should have a agg_nonce and a sighash
    r_agg = nonce_response['payload']['r_agg']
    sig_hash = nonce_response['payload']['sig_hash']
    should_negate_nonce = nonce_response['payload']['negated']

    wallet.set_r_agg(r_agg)
    wallet.set_sig_hash(sig_hash)
    wallet.set_should_negate_nonce(should_negate_nonce)

    partial_signature = wallet.sign_with_current_context(nonce)
    print("Providing partial signatuire: ", partial_signature)

    #Provide cordinator with partial sig
    nonce_payload = generate_nostr_message(command='sign', req_id=req_id, payload={
                                                 'spend_request_id': spend_request_id, 'signature': partial_signature})
    construct_and_publish_event(
        nonce_payload, private_key, relay_manager)

    print('Nostr payload sent to cordinator, awaiting response')
    # Wait for a bit, ideally this is a expoentially backoff waiting period where we timeout after n tries
    time.sleep(CORDINATOR_TIMEOUT)
    sign_response = None
    # Here we want to wait for other signers to provide their nonces
    while 1:
        if not relay_manager.message_pool.has_events():
            print("Waiting for other signers to send signatures... ")
            time.sleep(5)

        payloads = read_cordinator_messages(
            relay_manager, private_key, time_stamp_filter=time_stamp)
        filtered_payloads = [payload for payload in payloads if payload['command']
                            == "sign" and payload['payload']['spend_request_id'] == spend_request_id]

        if len(filtered_payloads) == 0:
            print('Cordinator did not respond to sign command')
            continue
        # Server shouldnt respond with > 1 notes
        sign_response = filtered_payloads[0]
        break

    if sign_response == None:
        print('Cordinator did not respond to spend command')
        return None
    raw_tx = sign_response['payload']['raw_tx']
    print(f"Got rawtx from cordinator {raw_tx}")
    return raw_tx

def setup_logging():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    logging.info(Fore.RED + header)

def run_signer(wallet_id=None, key_pair_seed=None, nonce_seed=None):
    setup_logging()

    relay_manager = add_relays()
    private_key = read_nsec()
    cordinator_pk = read_cordinator_pk()
    init_relay_manager(relay_manager, [cordinator_pk])
    print('Relay manager started')
    wallet = None
    if wallet_id != None:
        wallet = Wallet(wallet_id=wallet_id, key_pair_seed=key_pair_seed, nonce_seed=nonce_seed)
        
    while True:
        user_input = input("Enter a command: ")
        if user_input.lower() == "new wallet":
            quorum = int(input("Enter a quorum: "))
            print(f"Creating a new wallet with {quorum} signers ...")
            wallet_id = handle_create_wallet(
                quorum, relay_manager, private_key)
            wallet = Wallet(wallet_id, key_pair_seed=key_pair_seed, nonce_seed=nonce_seed)
        elif user_input.lower() == "send pk":
            print("Generating and posting the public key...")
            handle_create_xpub(wallet, relay_manager, private_key)
        elif user_input.lower() == "address":
            # TODO bug: you cannot sign or spend with out getting an address first
            print("Generating a new address...")
            address_payload = handle_get_address(
                wallet, 0, relay_manager, private_key)

            wallet.set_cmap(address_payload['cmap'])
            wallet.set_pubkey_agg(address_payload['pubkey_agg'])
            print(f"Got address {address_payload['address']}")

        elif user_input.lower() == "spend":
            print("Preparing to spend funds...")
            txid = input("Enter previous tx id: ")
            index = int(input("Enter output index: "))
            new_address = input("Where would you like to send sats to: ")
            sats = int(input("How much are we spending: "))

            spend_request_id = handle_spend(
                [txid, index], new_address, sats, wallet, relay_manager, private_key)
            wallet.set_current_spend_request_id(spend_request_id)
            print(
                f'Your spend request id {spend_request_id}, next provide nonces and signatures!!')
        elif user_input.lower() == "sign":
            spend_request_id = input("Provide a spend request id: ")
            spend_request_id = handle_sign_tx(
                spend_request_id, wallet, relay_manager, private_key)
        else:
            print("Invalid command. Please enter one of the following: 'new wallet', 'send pk', ' address', 'spend', 'sign'")