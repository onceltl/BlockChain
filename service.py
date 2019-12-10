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


    def get_block_num(self, peer):
        # TODO: get block num from peer
        # return -1 if unreachable
        return -1


    def update_verified_txns(self):
        with self.verified_txns_mutex:
            self.verified_txns = {}
            with self.mutex:
                for blk in self.blocks:
                    for txn in blk.tr_list:
                        self.verified_txns[utils.get_hash(txn)] = 1
        # print(self.verified_txns)


    def verify_txn(self, txn):
        # print("verify", utils.get_hash(txn), utils.get_hash(txn) in self.verified_txns)
        if utils.get_hash(txn) in self.verified_txns:
            return False
        return True


    def verify_block(self, blk):
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


    def get_block(self, peer, idx):
        # TODO: get block from peer
        blk = block.Block()
        self.valid_block(blk)
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

            max_peer = (-1, 0)
            for candidate in candidates:
                if candidate[1] > max_peer[1]:
                    max_peer = candidate[1]

            if max_peer[0] != -1:
                # Sync blocks to peer
                peer = max_peer[0]
                remote_blocks = []
                local_tail = len(self.blocks) - 1
                remote_head = len(self.blocks)
                remote_tail = local_tail + max_peer[1]

                # Get remote blocks
                for idx in range(remote_tail, remote_head, -1):
                    remote_block = self.get_block(peer, idx)
                    if remote_block == None:
                        return
                    remote_blocks.append(remote_block)
                # Validate remote blocks
                if len(remote_blocks) > 0:
                    for i in range(len(remote_blocks) - 1):
                        pre_hash = utils.get_hash(remote_blocks[i + 1])
                        if pre_hash != remote_blocks[i].pre_hash:
                            return

                while (local_tail >= 0):
                    remote_block = self.get_block(peer, remote_head)
                    if remote_block == None:
                        return
                    # Validate remote block
                    if len(remote_blocks) > 0:
                        pre_hash = utils.get_hash(remote_block)
                        if pre_hash != remote_blocks[-1].pre_hash:
                            return
                    tail_hash = utils.get_hash(self.blocks[local_tail])
                    if tail_hash == remote_block.pre_hash:
                        break
                    local_tail -= 1
                    remote_head -= 1
                
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
            for _ in range(times):
                nonce = int(random.random() * pow(2, 64))
                self.current_block.set_nonce(nonce)
                if self.verify_block(self.current_block):
                    print("Mining Success!")
                    self.current_block.output()
                    # print(len(self.blocks))
                    with self.mutex:
                        self.blocks.append(self.current_block)
                    peer_num = min(self.peer_num, len(self.peers))
                    peers = random.sample(self.peers, peer_num)
                    for peer in peers:
                        res = self.send_block(peer, self.current_block)
                        if res == -1:
                            self.peers.remove(peer)
                    break


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

        def func(signum, frame):
            self.exit_flag = True
        signal.signal(signal.SIGINT, func)

        # TODO: prepare and start RPC server

        # self.loop(1, self.handle_update)
        self.loop(1, self.mine)
        # self.loop(1, self.handle_pending)

        # cnt = 0
        while not self.exit_flag:
            time.sleep(1)

            # cnt += 1
            # if cnt == 5:
            #     from trans import Txin, Txout, Transaction
            #     txin = Txin(0, 0, 0, 0)
            #     txout = Txout("addr", 1)
            #     txins = [txin]
            #     txouts = [txout]
            #     tx2 = Transaction(txins, [txout, txout], 100, 3)
            #     self.pending_transactions.append(tx2)


if __name__ == "__main__":
    service = Service()
    # service.start()

    # p = Peer("127.0.0.1", 6379)
    # print(p.get_bind())

    # TODO: Initial Block

    from trans import *
    txin = Txin(0, 0, 0, 0)
    txout = Txout("addr", 1)
    txins = [txin]
    txouts = [txout]
    tx = Transaction(txins, txouts, 100, 3)
    tx2 = Transaction(txins, [txout, txout], 100, 3)

    service.pending_transactions = [tx]
    # print(len(service.addr))
    service.start()
    # service.mine()
    # service.update_verified_txns()
    # blk = service.current_block
    # print(service.valid_block(blk))
    # service.current_block.output()
