import logging

from src.utils.nostr_utils import add_relays, init_relay_manager, read_nsec, read_public_keys

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
