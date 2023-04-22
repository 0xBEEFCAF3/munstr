import json
import logging
import time

from src.utils.nostr_utils import add_relays, init_relay_manager, read_nsec, read_public_keys
from src.utils.payload import is_valid_json, is_valid_payload

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

def setup_logging():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    logging.info(header)

def run():
    setup_logging()

    relay_manager = add_relays()
    nostr_private_key, nostr_public_key = read_nsec('src/coordinator/nsec.txt')

    # get the public keys for the signers so we can subscribe to messages from them
    signer_pks = read_public_keys('src/coordinator/signer_pks.txt')

    init_relay_manager(relay_manager, signer_pks)

    while 1:
        if (not relay_manager.message_pool.has_events()):
            logging.info('No messages! Sleeping ZzZzZzzz...')
            time.sleep(1)
            continue

        new_event = relay_manager.message_pool.get_event()
        event_content = new_event.event.content
        # print(f"Message content: {event_content}")
        # print(f"From Public key {new_event.event.public_key}")

        if (not is_valid_json(event_content)):
            logging.info('Error with new event! Invalid JSON')
            continue

        json_payload = json.loads(event_content)
        if (not is_valid_payload(json_payload)):
            logging.info('Error with new event! Payload does not have the required keys')
            continue


