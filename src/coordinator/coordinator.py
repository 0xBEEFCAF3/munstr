import json
import logging
import time

from colorama import Fore

from src.utils.nostr_utils import show_relays, add_relays, construct_and_publish_event, generate_nostr_message, init_relay_manager, read_nsec, read_public_keys
from src.utils.payload import is_valid_json, is_valid_payload, PayloadKeys
from src.coordinator.wallet import add_xpub, create_wallet, is_valid_command, get_address, save_nonce, start_spend, save_signature
from src.coordinator.db import DB

header = """
 ▄████▄   ▒█████   ▒█████   ██▀███  ▓█████▄  ██▓ ███▄    █  ▄▄▄     ▄▄▄█████▓ ▒█████   ██▀███  
▒██▀ ▀█  ▒██▒  ██▒▒██▒  ██▒▓██ ▒ ██▒▒██▀ ██▌▓██▒ ██ ▀█   █ ▒████▄   ▓  ██▒ ▓▒▒██▒  ██▒▓██ ▒ ██▒
▒▓█    ▄ ▒██░  ██▒▒██░  ██▒▓██ ░▄█ ▒░██   █▌▒██▒▓██  ▀█ ██▒▒██  ▀█▄ ▒ ▓██░ ▒░▒██░  ██▒▓██ ░▄█ ▒
▒▓▓▄ ▄██▒▒██   ██░▒██   ██░▒██▀▀█▄  ░▓█▄   ▌░██░▓██▒  ▐▌██▒░██▄▄▄▄██░ ▓██▓ ░ ▒██   ██░▒██▀▀█▄  
▒ ▓███▀ ░░ ████▓▒░░ ████▓▒░░██▓ ▒██▒░▒████▓ ░██░▒██░   ▓██░ ▓█   ▓██▒ ▒██▒ ░ ░ ████▓▒░░██▓ ▒██▒
░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░ ▒▒▓  ▒ ░▓  ░ ▒░   ▒ ▒  ▒▒   ▓▒█░ ▒ ░░   ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░
  ░  ▒     ░ ▒ ▒░   ░ ▒ ▒░   ░▒ ░ ▒░ ░ ▒  ▒  ▒ ░░ ░░   ░ ▒░  ▒   ▒▒ ░   ░      ░ ▒ ▒░   ░▒ ░ ▒░
░        ░ ░ ░ ▒  ░ ░ ░ ▒    ░░   ░  ░ ░  ░  ▒ ░   ░   ░ ░   ░   ▒    ░      ░ ░ ░ ▒    ░░   ░ 
░ ░          ░ ░      ░ ░     ░        ░     ░           ░       ░  ░            ░ ░     ░     
░                                    ░                                                         
"""

# Map application commands to the corresponding methods
COMMAND_MAP = {
    'address':  get_address,
    'nonce':    save_nonce,
    'spend':    start_spend,
    'sign':     save_signature,
    'wallet':   create_wallet,
    'xpub':     add_xpub
}

def setup_logging():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    logging.info(Fore.GREEN + header)

def run(show, relays):
    setup_logging()

    # start up the db
    db = DB('src/coordinator/db.json')

    if show:
        print("----- ACTIVE RELAYS -----\n")
        show_relays()
        exit()

    relay_manager = add_relays(relays)
    nostr_private_key, nostr_public_key = read_nsec('src/coordinator/nsec.txt')

    # get the public keys for the signers so we can subscribe to messages from them
    signer_pks = read_public_keys('src/coordinator/signer_pks.txt')

    init_relay_manager(relay_manager, signer_pks)

    # initialize a timestamp filter
    # this will be used to keep track of messages that we have already seen
    timestamp_filter = int(time.time())

    while 1:
        if (not relay_manager.message_pool.has_events()):
            logging.info('No messages! Sleeping ZzZzZzzz...')
            time.sleep(1)
            continue

        new_event = relay_manager.message_pool.get_event()
        event_content = new_event.event.content
        # print(f"Message content: {event_content}")
        # print(f"From Public key {new_event.event.public_key}")

        #
        # Event validation
        #
        if (not is_valid_json(event_content)):
            logging.info('Error with new event! Invalid JSON')
            continue

        json_payload = json.loads(event_content)
        if (not is_valid_payload(json_payload)):
            logging.info('Error with new event! Payload does not have the required keys')
            continue

        command = json_payload['command']
        if (not is_valid_command):
            logging.info('%s is not a valid command!', command)
            continue

        # skip if this event is old
        event_timestamp = json_payload[PayloadKeys.TIMESTAMP.value]
        if (event_timestamp < timestamp_filter):
            continue

        #
        # Handle the command that's in the event
        #
        try:
            logging.info('[coordinator] Handling command of type: %s', command)
            result = COMMAND_MAP[command](json_payload['payload'], db)

            # package the result into a response
            ref_id = json_payload[PayloadKeys.REQUEST_ID.value]
            response_payload = {}

            if command == "wallet":
                response_payload = {
                    'wallet_id': result
                }
            elif command == "address":
                response_payload = {
                    'address':      result[0],
                    'cmap':         result[1],
                    'pubkey_agg':   result[2]
                }
            elif command == "spend":
                response_payload = {
                    'spend_request_id': result
                }
            elif command == "nonce":
                if result != None: 
                    response_payload = {
                        'r_agg':    result[0],
                        'sig_hash': result[1],
                        'negated':  result[2],
                        'spend_request_id': json_payload['payload']['spend_request_id']
                    }
            elif command == "sign":
                if (result != None):
                    response_payload = {
                        'raw_tx':   result,
                        'spend_request_id': json_payload['payload']['spend_request_id']
                    }
            if result != None:
                nostr_response = generate_nostr_message(command=command, ref_id=ref_id, payload=response_payload)
                construct_and_publish_event(nostr_response, nostr_private_key, relay_manager)

        except Exception as e:
            logging.error('Something went wrong!')
            print(e)
            pass
            # TODO better error handling

        # update the timestamp filter to keep track of messages we have already seen
        timestamp_filter = int(time.time())
