# 🕸🕯munstr🕯🕸 

A terminal based wallet that combines the powers of MuSig and Nostr.

Munstr uses MuSig to create and spend from k-of-k multisignature addresses. To anyone observing the blockchain, the transactions look like single key P2TR spends.

Nostr is used as the communication protocol. It's how signers talk to the coordinator.

## Getting started

1. Start virtualenv `python3 -m venv .venv`
2. `pip3 install -r requirements.txt`

### Running the coordinator

`python3 start_coordinator.py`

### Running a signer

`python3 start_signer.py`

## Standing on the shoulders of giants

In addition to the libraries listed in `requirements.txt`, this project also uses:

- Code from the Bitcoin Optech Taproot & Schnorr workshop, specifically the Python test framework. The `test_framework` folder has been brought into our project and renamed to `src/bitcoin`.
