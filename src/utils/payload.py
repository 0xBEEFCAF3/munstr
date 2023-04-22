import json
import logging

def is_valid_json(json_str: str):
    try:
        json.loads(json_str)
    except ValueError as e:
        logging.error("Invalid JSON!")
        print(e)
        return False
    return True

def is_valid_payload(payload: dict):
    # ref_id is also valid but not required
    required_keys = ['req_id', 'command', 'payload', 'ts']

    for key in required_keys:
        if key not in list(payload.keys()):
            logging.error("Key is missing from JSON payload: %s", key)
            return False

    return True