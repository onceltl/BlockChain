from merkle_tree import MerkleTree
import utils

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
        self.nonce = 0
    
        self.tr_list = tr_list

        mt = MerkleTree(self.tr_list)
        if len(tr_list) > 0:
            self.mt_root = mt.root_val
        else:
            self.mt_root = utils.get_hash(None)
    

    def set_nonce(self, nonce):
        self.nonce = nonce

    
    def set_ts(self, ts):
        self.ts = ts

    
    def output(self):
        print("Block:", self.idx, "ver: ", self.ver, "time_stamp: ", self.ts, "fee", self.fee, "thresh", self.thresh)
        print("pre_hash: ", self.pre_hash[:8])
        print("addr: ", self.addr[:8])
        print("mr_root: ", self.mt_root[:8])
        print("nonce: ", self.nonce)
        print("hash: ", utils.get_hash(self)[:8])
        print("Fin.")


if __name__ == "__main__":
    pass
