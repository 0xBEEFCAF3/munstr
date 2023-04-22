import json
import os

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # If obj is a UUID, serialize it to a string
            return str(obj)
        # For all other objects, use the default serialization method
        return super().default(obj)

class DB:
    def __init__(self, json_file):
        if not os.path.isfile(json_file):
            raise FileNotFoundError(f"JSON file '{json_file}' not found")
        self.json_file = json_file

    def get_data(self):
        with open(self.json_file, "r") as f:
            return json.load(f)

    def set_data(self, new_data):
        with open(self.json_file, "w") as f:
            json.dump(new_data, f)

    def get_value(self, key):
        with open(self.json_file, "r") as f:
            data = json.load(f)
        return data.get(key)

    def set_value(self, key, value):
        with open(self.json_file, "r") as f:
            data = json.load(f)
        data[key] = value
        with open(self.json_file, "w") as f:
            json.dump(data, f)

    ## TODO these utility functions should reside in their own file

    def add_wallet(self, wallet_id, quorum):
        with open(self.json_file, "r") as f:
            data = json.load(f)

        filtered = [wallet for wallet in data['wallets'] if wallet['wallet_id'] == wallet_id]
        if len(filtered) > 0:
            return False
        data['wallets'].append({'wallet_id': wallet_id, 'quorum': quorum})
        with open(self.json_file, "w") as f:
            json.dump(data, f)

        return True
    
    def get_wallet(self, wallet_id):
        with open(self.json_file, "r") as f:
            data = json.load(f)
        filtered = [wallet for wallet in data['wallets'] if wallet['wallet_id'] == wallet_id]
        if len(filtered) > 0:
            return filtered[0]
        return None

    def get_xpubs(self, wallet_id):
        with open(self.json_file, "r") as f:
            data = json.load(f)
        filtered = [xpub for xpub in data['xpubs'] if xpub['wallet_id'] == wallet_id]
        if len(filtered) > 0:
            return filtered
        return None

    def add_xpub(self, wallet_id, xpub):
        with open(self.json_file, "r") as f:
            data = json.load(f)
        # TODO check wallet id exists
        filtered_xpubs = [xpub for xpub in data['xpubs'] if xpub['wallet_id'] == wallet_id and xpub['xpub'] == xpub]
        if len(filtered_xpubs) > 0:
            return False

        data['xpubs'].append({'wallet_id': wallet_id, 'xpub': xpub})

        with open(self.json_file, "w") as f:
            json.dump(data, f)

        return True

    def add_spend_request(self, txid, output_index, prev_script_pubkey, spend_request_id, new_address):
        with open(self.json_file, "r") as f:
            data = json.load(f)
        filtered = [spend for spend in data['spends'] if spend['spend_request_id'] == spend_request_id]
        if len(filtered) > 0:
            return False
        data['spends'].append({'spend_request_id': spend_request_id, 'txid': txid, 'output_index': output_index, 'prev_script_pubkey': prev_script_pubkey, 'new_address': new_address})
        with open(self.json_file, "w") as f:
            json.dump(data, f)

        return True
        

    def add_nonce(self, nonce, spend_request_id):
        with open(self.json_file, "r") as f:
            data = json.load(f)
        # TODO should protect the same nonce being provided again
        data['nonces'].append({'spend_request_id': spend_request_id, 'nonce': nonce})
        with open(self.json_file, "w") as f:
            json.dump(data, f)

        return True 