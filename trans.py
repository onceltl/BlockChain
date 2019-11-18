import utils

class Txin:
    def __init__(self, pre_tx_hash, pre_txout_idx, pre_txout_key, pre_txout_sig):
        # hash of pre transaction
        self.pre_tx_hash = pre_tx_hash
        # index of txout in pre transaction
        self.pre_txout_idx = pre_txout_idx
        # public key of txout in pre transaction
        self.pre_txout_key = pre_txout_key
        # signature of txout in pre transaction
        self.pre_txout_sig = pre_txout_sig

class Txout:
    def __init__(self, addr, val):
        self.addr = addr
        self.val = val

class Transaction:
    def __init__(self, txins, txouts, ts, fee):
        self.txins = txins
        self.txouts = txouts
        self.ts = ts
        self.fee = fee
        
    def sign(self, txout_idx, key_private):
        return utils.sign(self, key_private)
