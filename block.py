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
    
        for tr in tr_list:
            self.fee += tr.fee
        
        # TODO: transaction in and out
        # fee_trans = Transaction()
        # self.tr_list = [fee_trans] + self.tr_list
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
        print("Block:")
        print("idx: ", self.idx)
        print("ver: ", self.ver)
        print("pre_hash: ", self.pre_hash)
        print("time_stamp: ", self.ts)
        print("fee: ", self.fee)
        print("thresh: ", self.thresh)
        print("addr: ", self.addr)
        print("mr_root: ", self.mt_root)
        print("nonce: ", self.nonce)
        print("hash: ", utils.get_hash(self))
        print("Fin.")


if __name__ == "__main__":
    pass
