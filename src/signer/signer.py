import logging

from colorama import Fore

from src.utils.nostr_utils import add_relays, init_relay_manager, read_nsec, read_public_keys

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

def setup_logging():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    logging.info(Fore.RED + header)

def run():
    setup_logging()

    relay_manager = add_relays()
    nostr_private_key, nostr_public_key = read_nsec('src/signer/nsec.txt')

    # get the coordinator public key so we can subscribe to messages from it
    coordinator_public_key = read_public_keys('src/signer/coordinator_pk.txt')

    init_relay_manager(relay_manager, coordinator_public_key)
