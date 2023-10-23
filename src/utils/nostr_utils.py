import json
import logging
import ssl
import time
import uuid
import requests
import sys
import random

from nostr.event import  Event, EventKind
from nostr.filter import Filter, Filters
from nostr.key import PrivateKey
from nostr.message_type import ClientMessageType
from nostr.relay_manager import RelayManager

from src.utils.payload import PayloadKeys

NOSTR_RELAYS = ["wss://nostr-pub.wellorder.net", "wss://relay.damus.io"]
NOSTR_WATCH = "https://api.nostr.watch/v1/online"

def shuffle_relays():
    if (input(f"Default relays: {NOSTR_RELAYS}\nShuffle more relays? y/n ")) == 'y':
        r = (requests.get(NOSTR_WATCH, {})).json()
        while(1):
            new_relays = [x for x in r[:15] if 'damus' not in x and 'nostr-pub.wellorder' not in x]

            if (ans := input(f"New online relays found:\n{new_relays}\nIs that OK? y/n/r (n to go back to original, r to reshuffle) ")) == 'y':
                for val in new_relays: 
                    NOSTR_RELAYS.append(val)
                break
            elif ans == 'r':
                random.shuffle(r)
            elif ans == 'n':
                break

def add_relays():
    relay_manager = RelayManager()
    [relay_manager.add_relay(relay) for relay in NOSTR_RELAYS]

    logging.info("[nostr] Added the following relay(s): %s", NOSTR_RELAYS)
    return relay_manager

def construct_and_publish_event(payload: dict, private_key: PrivateKey, relay_manager: RelayManager):
    public_key = private_key.public_key
    event = Event(content=json.dumps(payload), public_key=public_key.hex())

    private_key.sign_event(event)
    relay_manager.publish_event(event)

    logging.info('[nostr] Published event for the %s command', payload[PayloadKeys.COMMAND.value])


# Used to generate both requests and responses
def generate_nostr_message(command: str, req_id=str(uuid.uuid4()), ref_id=None, payload={}):
    message = {
        PayloadKeys.COMMAND.value:      command,
        PayloadKeys.REQUEST_ID.value:   req_id,
        PayloadKeys.PAYLOAD.value:      payload,
        PayloadKeys.TIMESTAMP.value:    int(time.time())
    }

    if (ref_id != None):
        message['ref_id'] = ref_id

    return message

def init_relay_manager(relay_manager: RelayManager, author_pks: list[str]):
    # set up relay subscription
    subscription_id = "str"
    filters = Filters([Filter(authors=author_pks, kinds=[EventKind.TEXT_NOTE])])
    relay_manager.add_subscription(subscription_id, filters)

    # NOTE: This disables ssl certificate verification
    relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE})

    # wait a moment for a connection to open to each relay
    time.sleep(1.5)

    request = [ClientMessageType.REQUEST, subscription_id]
    request.extend(filters.to_json_array())
    message = json.dumps(request)

    relay_manager.relays[NOSTR_RELAYS[0]].publish(message)

    # give the message a moment to send
    time.sleep(1)

    logging.info("[nostr] Relay manager started!")

# read an nsec from a file, return both private and public keys
def read_nsec(nsec_file_name):
    with open(nsec_file_name, 'r') as f:
        try:
            nsec = f.read()
            private_key = PrivateKey().from_nsec(nsec)
            public_key = private_key.public_key.hex()
            logging.info("[nostr] My public key: %s", public_key)
            return private_key, public_key
        except Exception:
            logging.error("[nostr] Unexpected error reading nsec from %s", nsec_file_name)
            sys.exit(1)

# read public keys from a file
def read_public_keys(file_name):
    with open(file_name, 'r') as f:
        try:
            lines = f.readlines()
            return [line.strip() for line in lines]
        except Exception:
            logging.error("[nostr] Unexpected error reading public keys from %s", file_name)
            sys.exit(1)

