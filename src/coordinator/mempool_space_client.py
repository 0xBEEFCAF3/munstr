import requests
import logging

API_ENDPOINT = "https://mempool.space/testnet/api"

def get_transaction(txid):
    get_transaction_path = f"/tx/{txid}"

    try:
        response = requests.get(API_ENDPOINT + get_transaction_path)
        response.raise_for_status()
        transaction = response.json()

        return transaction
    except requests.exceptions.RequestException as e:
        logging.error("[mempool.space client] Error retrieving transaction %s", txid)
        print(e)
        return None