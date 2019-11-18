from merkle_tree import MerkleTree


# Defination of Block
# ts: time stamp
class Block:
    def __init__(self, idx, ver, pre_hash, ts, fee, tr_list, thresh, addr):
        self.idx = idx
        self.ver = ver
        self.pre_hash = pre_hash
        self.ts = ts
        self.fee = fee
        self.thresh = thresh
        self.addr = addr
    
        for tr in tr_list:
            self.fee += tr.fee
        
        # TODO: transaction in and out
        # fee_trans = Transaction()
        # self.tr_list = [fee_trans] + self.tr_list
        self.tr_list = tr_list

        mt = MerkleTree(self.tr_list)
        self.mt_root = mt.root_val
    

    def set_nonce(self, nonce):
        self.nonce = nonce

    
    def set_ts(self, ts):
        self.ts = ts


if __name__ == "__main__":
    pass
