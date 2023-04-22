import uuid

COMMANDS = ['wallet']

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
