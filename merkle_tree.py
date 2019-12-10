import crypto
import math
import utils


# Node in a Merkle Tree.
class Node:
    def __init__(self, typ, dep, val, ls = -1, rs = -1):
        self.typ = typ
        self.dep = dep
        self.val = val
        self.ls = ls
        self.rs = rs


class MerkleTree:
    def __init__(self, tr_list):
        self.tr_n = len(tr_list)
        if self.tr_n == 0:
            return None
        
        dep = math.ceil(math.log(self.tr_n, 2))
        self.nodes = []
        for tr in tr_list:
            tr_hash = utils.get_hash(tr)
            self.nodes.append(Node(0, dep, tr_hash))
        for _ in range(self.tr_n, 2 ** dep):
            self.nodes.append(self.nodes[self.tr_n - 1])
        
        st = 0
        for i in range(dep - 1, -1, -1):
            for j in range(0, 2 ** i):
                h0 = self.nodes[st + 2 * j].val
                h1 = self.nodes[st + 2 * j + 1].val
                h = utils.get_hash(str(h0) + str(h1))
                self.nodes.append(Node(1, i, h, st + 2 * j, st + 2 * j + 1))
            st += 2 ** (i + 1)
        self.root = len(self.nodes) - 1
        self.root_val = self.nodes[self.root].val


# for test
if __name__ == "__main__":
    from trans import *
    txin = Txin(0, 0, 0, 0)
    txout = Txout("addr", 1)
    txins = [txin]
    txouts = [txout]
    tx = Transaction(txins, txouts, 100, 3)
    tr_list = [tx]
    mt = MerkleTree(tr_list)
    # for i in range(0, 4):
    #     print(utils.get_hash(utils.get_hash(tr_list[2*i]) + utils.get_hash(tr_list[2*i+1])))
    # for node in mt.nodes:
    #     print(node.typ, node.val)
    print(mt.root_val)
    
