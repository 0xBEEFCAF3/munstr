from src.signer.signer import run_signer

import sys
import argparse


def main(wallet_id=None, key_pair_seed=None, nonce_seed=None):
    run_signer(wallet_id=wallet_id, key_pair_seed=key_pair_seed, nonce_seed=nonce_seed)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--wallet_id", help="Wallet ID", default=None)
    parser.add_argument("--key_seed", help="Key seed")
    parser.add_argument("--nonce_seed", help="Nonce seed")
    args = parser.parse_args()

    # Call the main function with the command line arguments
    main(args.wallet_id, args.key_seed, args.nonce_seed)

