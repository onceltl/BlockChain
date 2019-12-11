import time
import signal
import random
import threading

import block
import utils
import crypto
import trans


class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.latency = 0
    
    
    def get_bind(self):
        return self.host + ":" + str(self.port)
    

    def set_latency(self, latency):
        self.latency = latency


class Service:
    def __init__(self):
        # Exit
        self.exit_flag = False

        # Peers
        self.peers = []
        self.peer_num = 3

        # Transaction
        self.key_private = crypto.gen_key_private()
        self.key_public = crypto.gen_key_public(self.key_private)
        self.addr = crypto.gen_addr(self.key_public)
        self.transaction_mutex = threading.Lock()
        self.pending_transactions = []

        # Mine
        self.ver = 0
        self.transaction_max_num = 10
        self.thresh = 3
        self.fee = 1024

        # Local blocks
        self.mutex = threading.Lock()
        self.blocks = []

        # Pending blocks
        self.pending_mutex = threading.Lock()
        self.pending_blocks = []

        # Current block
        self.current_mutex = threading.Lock()
        self.current_block = None

        # Verified Txns
        self.verified_txns_mutex = threading.Lock()
        self.verified_txns = {}

        # For testing
        self.tmp_chain = []


    def get_block_num(self, peer):
        # TODO: get block num from peer
        # return -1 if unreachable
        # for testing
        if peer == "test_peer":
            return len(self.tmp_chain)
        return -1


    def print_chain(self):
        with self.mutex:
            if len(self.blocks) == 0:
                return
            print(utils.get_hash(self.blocks[0])[:8], end="")
            for i in range(1, len(self.blocks)):
                print("->", utils.get_hash(self.blocks[i])[:8], end="")
            print()
    
    def print_blocks(self, blocks):
        if len(blocks) == 0:
            return
        print(utils.get_hash(blocks[0])[:8], end="")
        for i in range(1, len(blocks)):
            print("->", utils.get_hash(blocks[i])[:8], end="")
        print()
        


    def update_verified_txns(self):
        with self.verified_txns_mutex:
            self.verified_txout_used = {}
            self.verified_txout = {}
            with self.mutex:
                for blk in self.blocks:
                    for txn in blk.tr_list:
                        self.verified_txout_used[utils.get_hash(txn)] = [False] * len(txn.txouts)
                        self.verified_txout[utils.get_hash(txn)] = txn.txouts
                        for txin in txn.txins:
                            if not txin.pre_tx_hash == None:
                                self.verified_txout_used[txin.pre_tx_hash][txin.pre_txout_idx] = True
        # print(self.verified_txns)


    def verify_txn(self, txn):
        # verify inside txn same txin
        txin_map = {}
        for txin in txn.txins:
            tmp1 = txin.pre_tx_hash
            tmp2 = txin.pre_txout_idx
            if tmp1 in txin_map and tmp2 in txin_map[tmp1]:
                print("Verification Failed: same txin.")
                txn.output()
                return False
            if tmp1 not in txin_map:
                txin_map[tmp1] = {}
            txin_map[tmp1][tmp2] = 1

        # verify txin in block chain
        for idx in range(len(txn.txins)):
            txin = txn.txins[idx]
            if not txin.pre_tx_hash in self.verified_txout:
                print("Verification Failed: pre_txn hash not existed.")
                print("pre_tx_hash:", txin.pre_tx_hash)
                txn.output()
                return False
            pre_txout_map = self.verified_txout_used[txin.pre_tx_hash]
            if txin.pre_txout_idx >= len(pre_txout_map):
                print("Verification Failed: pre_idx hash not existed.")
                print("pre_txout_idx:", txin.pre_txout_idx)
                txn.output()
                return False
            if pre_txout_map[txin.pre_txout_idx] == True:
                print("Verification Failed: pre_txout used.")
                txn.output()
                return False

        # verify tot in and out
        totin = 0
        totout = 0
        fee_flag = False
        for txin in txn.txins:
            if txin.pre_tx_hash != None:
                totin += self.verified_txout[txin.pre_tx_hash][txin.pre_txout_idx].val
            else:
                fee_flag = True
        for txout in txn.txouts:
#            if txout.addr != None:
            totout += txout.val
        if totin != totout:
            print("Verification Failed: in and out don't match.", totin, totout)
            return False

        print("Verification Succeed!", fee_flag, totin, totout)

        return True

    def verify_block_nonce(self, blk):
        try:
            if not isinstance(blk, block.Block):
                return False
            h = utils.get_hash(blk)
            for i in range(blk.thresh):
                if h[i] != "0":
                    return False
            return True
        except Exception:
            return False


    # TODO: verify block.
    def verify_block(self, blk):
        return self.verify_block_nonce(blk)


    def get_block(self, peer, idx):
        # TODO: get block from peer
        # blk = block.Block()
        if peer == "test_peer":
            if idx >= len(self.tmp_chain):
                return None
            blk = self.tmp_chain[idx]
        if not self.verify_block(blk):
            return None
        return blk
    

    def handle_get_block(self, idx):
        try:
            with self.mutex:
                blk = self.blocks[idx]
            return blk
        except Exception:
            return None


    def send_block(self, peer, blk):
        # TODO: send block to peer
        return -1


    # handle send_block request
    def handle_send_block(self, blk):
        if not self.verify_block(blk):
            return
        with self.mutex:
            idx = len(self.blocks)
            if idx != blk.idx:
                return
            if idx > 0:
                pre_hash = utils.get_hash(self.blocks[-1])
            else:
                pre_hash = utils.get_hash(None)
            if pre_hash != blk.pre_hash:
                return
            self.blocks.append(blk)
        return


    def handle_update(self):
        with self.mutex:
            len_local = len(self.blocks)
            peer_num = min(self.peer_num, len(self.peers))
            peers = random.sample(self.peers, peer_num)
            candidates = []
            for peer in peers:
                len_remote = self.get_block_num(peer)
                if len_remote == -1:
                    self.peers.remove(peer)
                if len_remote > len_local:
                    candidates.append((peer, len_remote - len_local))
            # print(candidates)

            max_peer = (None, 0)
            for candidate in candidates:
                if candidate[1] > max_peer[1]:
                    max_peer = candidate

            # print(max_peer)
            if max_peer[0] == None:
                return

            # Sync blocks to peer
            peer = max_peer[0]
            remote_blocks = []
            local_tail = len(self.blocks) - 1
            remote_head = len(self.blocks)
            remote_tail = local_tail + max_peer[1]
            # print("Update: ", peer, local_tail, remote_head, remote_tail)

            # Get remote blocks
            for idx in range(remote_tail, remote_head - 1, -1):
                remote_block = self.get_block(peer, idx)
                if remote_block == None:
                    return
                remote_blocks.append(remote_block)

            # Verify remote blocks
            for i in range(len(remote_blocks) - 1):
                pre_hash = utils.get_hash(remote_blocks[i + 1])
                if pre_hash != remote_blocks[i].pre_hash:
                    return
            for blk in remote_blocks:
                if not self.verify_block(blk):
                    return

            while (local_tail >= 0):
                # print("Update in chain: ", local_tail)
                # self.print_blocks(remote_blocks)
                pre_hash = utils.get_hash(self.blocks[local_tail])
                # print(pre_hash[:8], remote_blocks[-1].pre_hash[:8])
                if remote_blocks[-1].pre_hash == pre_hash:
                    break
                # Branch
                remote_block = self.get_block(peer, local_tail)
                if remote_block == None:
                    return
                # Validate remote block
                pre_hash = utils.get_hash(remote_block)
                # print(pre_hash[:8], remote_blocks[-1].pre_hash[:8])
                if pre_hash != remote_blocks[-1].pre_hash:
                    return
                remote_blocks.append(remote_block)
                local_tail -= 1
                remote_head -= 1
            
            # print("Update in chain: ")
            # self.print_blocks(remote_blocks)
            # Update local blocks
            self.blocks = self.blocks[0:remote_head]
            rollback_num = len(remote_blocks)
            for i in range(rollback_num):
                self.blocks.append(remote_blocks[rollback_num - i - 1])


    def update_current_block(self):
        with self.transaction_mutex:
            self.pending_transactions.sort(key=lambda t:-t.fee)
            transactions = []
            for i in range(min(len(self.pending_transactions), self.transaction_max_num)):
                transaction = self.pending_transactions[i]
                if self.verify_txn(transaction):
                    transactions.append(transaction)
        
        # print("current txns: ", len(transactions))
        # for txn in transactions:
        #     print(utils.get_hash(txn)[:8])
        with self.mutex:
            idx = len(self.blocks)
            if idx == 0:
                pre_hash = utils.get_hash(None)
            else:
                pre_hash = utils.get_hash(self.blocks[-1])

        # Generate fee Transaction
        fee = self.fee
        for txn in transactions:
            fee += txn.fee
        txn_list = [trans.gen_fee_txn(fee)]
        for txn in transactions:
            txn_list.append(txn)
        # print(fee)

        self.current_block = block.Block(
            idx = idx,
            ver = self.ver,
            pre_hash = pre_hash,
            ts = int(time.time()),
            fee = fee,
            tr_list = txn_list,
            thresh = self.thresh,
            addr = self.addr
        )

    # Mining
    def mine(self):
        with self.current_mutex:
            self.update_verified_txns()
            self.update_current_block()
            times = 2 ** (self.thresh * 4)
            # while(True):
            for _ in range(times):
                nonce = int(random.random() * pow(2, 64))
                self.current_block.set_nonce(nonce)
                if self.verify_block_nonce(self.current_block):
                    print("Mining Success!", utils.get_hash(self.current_block)[:8])
                    # self.current_block.output()
                    # print(len(self.blocks))
                    with self.mutex:
                        self.blocks.append(self.current_block)
                    peer_num = min(self.peer_num, len(self.peers))
                    peers = random.sample(self.peers, peer_num)
                    for peer in peers:
                        res = self.send_block(peer, self.current_block)
                        if res == -1:
                            self.peers.remove(peer)
                    return
            print("Mining Failed.")
            


    def handle_pending(self):
        with self.pending_mutex:
            if len(self.pending_blocks) == 0:
                return
            else:
                blk = self.pending_blocks.pop(0)

        peer_num = min(self.peer_num, len(self.peers))
        peers = random.sample(self.peers, peer_num)
        for peer in peers:
            res = self.send_block(peer, blk)
            if res == -1:
                self.peers.remove(peer)


    # Run func and sleep for 'sleep_time' seconds.
    def loop(self, sleep_time, func, *args):
        func(*args)
        if not self.exit_flag:
            timer = threading.Timer(sleep_time, self.loop, (sleep_time, func) + args)
            timer.start()
    

    def start(self):
        # TODO: handle P2P latency
        # TODO: prepare and start RPC server

        self.loop(1, self.handle_update)
        self.loop(1, self.mine)
        # self.loop(1, self.handle_pending)

        while not self.exit_flag:
            tmp = input()
            cmd = tmp.strip().split()
            if cmd[0] == "exit":
                self.exit_flag = True
                continue
            if cmd[0] == "trans":
                if len(cmd) < 3:
                    print("not enough parameter")
                print(cmd)
                continue
            if cmd[0] == "chain":
                self.print_chain()


        # Test for update
        # for _ in range(5):
        #     self.mine()
        #     # time.sleep(1)
        # self.print_chain()
        
        # self.tmp_chain = []
        # with self.mutex:
        #     for blk in self.blocks:
        #         self.tmp_chain.append(blk)
        #     self.blocks = self.blocks[:1]
        # self.print_chain()
        # # print(self.get_block_num("test_peer"))
 
        # for _ in range(2):
        #     self.mine()
        #     # time.sleep(1)
        # self.print_chain()
        
        # self.peers = ["test_peer"]
        # self.handle_update()
        # self.print_chain()

        # Test for Transaction
        # cnt = 0
        # while not self.exit_flag:
        #     time.sleep(1)
        #     with self.mutex:
        #         print(len(self.blocks))
            # cnt += 1

            # if cnt == 2:
            #     from trans import Txin, Txout, Transaction
            #     txin = Txin(utils.get_hash(self.blocks[0].tr_list[0]), 0, self.key_public, None)
            #     txout1 = Txout(None, 3)
            #     txout2 = Txout(self.addr, 1022)
            #     txins = [txin]
            #     txouts = [txout1, txout2]
            #     tx2 = Transaction(txins, txouts, 100, 3)
            #     self.pending_transactions.append(tx2)


if __name__ == "__main__":
    service = Service()
    # service.start()

    # p = Peer("127.0.0.1", 6379)
    # print(p.get_bind())

    # from trans import Txin, Txout, Transaction
    # txin = Txin("aaaaaaaa", 3, 0, 0)
    # txout = Txout("addr", 1)
    # txins = [txin]
    # txouts = [txout]
    # tx = Transaction(txins, txouts, 100, 3)
    # tx2 = Transaction(txins, [txout, txout], 100, 3)

    # service.pending_transactions = [tx]
    # print(len(service.addr))
    service.start()
    # service.mine()
    # service.update_verified_txns()
    # blk = service.current_block
    # print(service.valid_block(blk))
    # service.current_block.output()
