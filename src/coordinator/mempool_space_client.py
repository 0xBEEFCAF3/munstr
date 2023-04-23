#
# Use mempool.space's API for interfacing with the network. In the future we
# would like users to be able to connect Munstr to their own node
#
import requests
import logging

API_ENDPOINT = "https://mempool.space/testnet/api"

def broadcast_transaction(tx_hex):
    broadcast_transaction_path = f"/tx"

    payload = {"tx": tx_hex}

    # TODO should data be set to tx_hex?
    response = requests.post(API_ENDPOINT + broadcast_transaction_path, data=payload)

    if (response.status_code == 200):
        logging.info('[mempool.space client] Transaction broadcast success!')
    else:
        logging.error('[mempool.space.client] Transaction broadcast failed with error code %d', response.status_code)
        logging.error(response.content)

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