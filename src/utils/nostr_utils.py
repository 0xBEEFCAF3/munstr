import json
import logging
import ssl
import time

from nostr.event import  Event, EventKind
from nostr.filter import Filter, Filters
from nostr.key import PrivateKey
from nostr.message_type import ClientMessageType
from nostr.relay_manager import RelayManager

NOSTR_RELAYS = ["wss://nostr-pub.wellorder.net", "wss://relay.damus.io"]

def add_relays():
    relay_manager = RelayManager()
    [relay_manager.add_relay(relay) for relay in NOSTR_RELAYS]

    logging.info("[nostr] Added the following relay(s): %s", NOSTR_RELAYS)
    return relay_manager

def init_relay_manager(relay_manager: RelayManager, author_pks: list[str]):
    # set up relay subscription
    subscription_id = "str"
    filters = Filters([Filter(authors=author_pks, kinds=[EventKind.TEXT_NOTE])])
    relay_manager.add_subscription(subscription_id, filters)

    # NOTE: This disables ssl certificate verification
    relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE})

    # wait a moment for a connection to open to each relay
    time.sleep(1.25)

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
        except(error):
            logging.error("[nostr] Unexpected error reading nsec from %s", nsec_file_name)
            sys.exit(1)

# read public keys from a file
def read_public_keys(file_name):
    with open(file_name, 'r') as f:
        try:
            lines = f.readlines()
            return [line.strip() for line in lines]
        except(error):
            logging.error("[nostr] Unexpected error reading public keys from %s", file_name)
            sys.exit(1)

