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

# for test
if __name__ == "__main__":
    txin = Txin(0, 0, 0, 0)
    txout = Txout("addr", 1)
    txins = [txin]
    txouts = [txout]
    tx = Transaction(txins, txouts, 100, 3)
    import crypto
    key_private = crypto.gen_key_private()
    key_public = crypto.gen_key_public(key_private)
    sig = tx.sign(0, key_private)
    print(utils.verify_sig(tx, sig, key_public))
