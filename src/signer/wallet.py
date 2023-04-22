from bip32 import BIP32, HARDENED_INDEX

from src.bitcoin.key import ECKey, ECPubKey, generate_key_pair, generate_bip340_key_pair, generate_schnorr_nonce
from src.bitcoin.messages import sha256, CTxInWitness, CScriptWitness
from src.bitcoin.musig import aggregate_musig_signatures, aggregate_schnorr_nonces, generate_musig_key, sign_musig
from src.bitcoin.script import tagged_hash
from src.bitcoin.script import CScript, CScriptOp, hash160, OP_0, OP_2, OP_CHECKMULTISIG, SegwitV0SignatureHash, SIGHASH_ALL, SIGHASH_ALL_TAPROOT, TaprootSignatureHash, get_p2pkh_script 
from src.bitcoin.address import program_to_witness
from src.bitcoin.messages import (
    COutPoint,
    CTransaction,
    CTxIn,
    CTxOut,
)

class Wallet:
    def __init__(self, wallet_id, key_pair_seed, nonce_seed):
        self.wallet_id = wallet_id
        self.nonce_seed = int(nonce_seed)
        
        self.private_key = None
        self.public_key = None
        self.cmap = None
        self.pubkey_agg = None
        self.r_agg = None
        self.should_negate_nonce = None

        self.current_spend_request_id = None
        self.sig_hash = None

        # TODO should use ascii or utf-8?
        prv, pk = generate_key_pair(sha256(bytes(key_pair_seed, 'ascii')))

        self.private_key = prv
        self.public_key = pk

    def get_root_xpub(self):
        return self.get_root_hd_node().get_xpub()
    
    def get_root_hd_node(self):
        key_bytes = self.private_key.get_bytes()
        return BIP32.from_seed(key_bytes)
    
    def get_pubkey_at_index(self, index: int):
        root_xpub = self.get_root_xpub()
        bip32_node = BIP32.from_xpub(root_xpub)
        pk = bip32_node.get_pubkey_from_path(f"m/{index}")

        key = ECPubKey().set(pk)
        return key.get_bytes()
    
    def get_new_nonce(self):
        k = ECKey().set(self.nonce_seed)
        return k.get_pubkey()

    def get_wallet_id(self):
        return self.wallet_id

    def set_cmap(self, cmap):
        modified_cmap = {}
        # Both key and value should be hex encoded strings
        # Key is public key
        # value is the challenge
        for key, value in cmap.items():
            modified_cmap[key] = bytes.fromhex(value)

        self.cmap = modified_cmap

    def get_pubkey(self):
        return self.public_key.get_bytes().hex()

    def set_pubkey_agg(self, pubkey_agg):
        self.pubkey_agg = ECPubKey().set(bytes.fromhex(pubkey_agg))

    def set_r_agg(self, r_agg):
        self.r_agg = ECPubKey().set(bytes.fromhex(r_agg))

    def set_should_negate_nonce(self, value):
        self.should_negate_nonce = value

    def set_sig_hash(self, sig_hash):
        self.sig_hash = bytes.fromhex(sig_hash)
    
    def set_current_spend_request_id(self, current_spend_request_id):
        self.current_spend_request_id = current_spend_request_id 

    def get_private_key_tweaked(self):
        if self.cmap != None:
            # TODO this is all bip32 stuff
            # TODO index is hardcoded at 1
            # index = 1
            # pk = self.get_pubkey_at_index(index).hex()
            # TODO hardcoded pk, get from class variable
            # prv = self.get_root_hd_node().get_privkey_from_path(f"m/{index}")
            # print("prv", prv)
            # private_key = ECKey().set(prv)

            pk = self.public_key.get_bytes().hex()
            private_key = self.private_key
            tweaked_key = private_key * self.cmap[pk]

            if self.pubkey_agg.get_y() % 2 != 0:
                tweaked_key.negate()
                self.pubkey_agg.negate()

            return tweaked_key
        return None

    def sign_with_current_context(self, nonce: str):
        if self.sig_hash == None or self.cmap == None or self.r_agg == None or self.pubkey_agg == None:
            # TODO should throw
            return None

        k1 = ECKey().set(self.nonce_seed)
        # negate here
        if self.should_negate_nonce:
            k1.negate()
        tweaked_private_key = self.get_private_key_tweaked()
        return sign_musig(tweaked_private_key, k1, self.r_agg, self.pubkey_agg, self.sig_hash)
    