from bip32 import BIP32

from src.bitcoin.key import ECKey, ECPubKey, generate_key_pair
from src.bitcoin.messages import sha256
from src.bitcoin.musig import sign_musig


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

    def get_private_key_tweaked(self, address_index: int):
        if self.cmap == None:
            return None
        pk = self.get_pubkey_at_index(address_index).hex()
        prv = self.get_root_hd_node().get_privkey_from_path(f"m/{address_index}")
        private_key = ECKey().set(prv)

        tweaked_key = private_key * self.cmap[pk]
        # TODO bug here where the server calcualtes a different y value and the signer
        if self.pubkey_agg.get_y() % 2 != 0:
            tweaked_key.negate()
            self.pubkey_agg.negate()

        return tweaked_key

    def sign_with_current_context(self, nonce: str, address_index: int):
        if self.sig_hash == None or self.cmap == None or self.r_agg == None or self.pubkey_agg == None:
            # TODO should throw
            return None

        k = ECKey().set(self.nonce_seed)
        # negate here
        if self.should_negate_nonce:
            k.negate()
        tweaked_private_key = self.get_private_key_tweaked(address_index)
        return sign_musig(tweaked_private_key, k, self.r_agg, self.pubkey_agg, self.sig_hash)
    
