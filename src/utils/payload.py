import json
import logging

from enum import Enum

# ref_id is also valid but not required
class PayloadKeys(Enum):
    REQUEST_ID = 'req_id'   # the request ID
    COMMAND = 'command'     # command to pass into the application
    PAYLOAD = 'payload'     # payload for the command
    TIMESTAMP = 'ts'        # timestamp

def is_valid_json(json_str: str):
    try:
        json.loads(json_str)
    except ValueError as e:
        logging.error("Invalid JSON!")
        print(e)
        return False
    return True

def is_valid_payload(payload: dict):
    required_keys = [payload_key.value for payload_key in PayloadKeys]
    for key in required_keys:
        if key not in list(payload.keys()):
            logging.error("Key is missing from JSON payload: %s", key)
            return False

    return True