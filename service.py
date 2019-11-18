import time
import signal
import random
import threading

import block
import utils
import crypto


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
        self.thresh = 10
        self.fee = 1024

        # Local blocks
        self.mutex = threading.Lock()
        self.blocks = []

        # Pending blocks
        self.pending_mutex = threading.Lock()
        self.pending_blocks = []
        self.current_block = None


    def get_block_num(self, peer):
        # TODO: get block num from peer
        # return -1 if unreachable
        return -1


    def valid_block(self, blk):
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
        if not self.valid_block(blk):
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
            t_num = 0
            # TODO: Add fee transaction
            transactions = []
            while len(self.pending_transactions) > 0 and t_num < self.transaction_max_num:
                transaction = self.pending_transactions.pop(0)
                if valid_transaction(transaction):
                    transactions.append(transaction)
        with self.mutex:
            idx = len(self.blocks)
            if idx == 0:
                pre_hash = utils.get_hash(None)
            else:
                pre_hash = utils.get_hash(self.blocks[-1])

        self.current_block = block.Block(
            idx = idx,
            ver = self.ver,
            pre_hash = pre_hash,
            ts = int(time.time()),
            fee = self.fee,
            tr_list = transactions,
            thresh = self.thresh,
            addr = self.addr
        )


    # Mining
    def mine(self):
        with self.mutex:
            self.update_current_block()
            times = 2 ** (self.thresh - 1)
            for _ in range(times):
                nonce = int(random.random() * pow(2, 64))
                self.current_block.set_nonce(nonce)
                if self.valid_block(self.current_block):
                    self.blocks.append(self.current_block)
                    peer_num = min(self.peer_num, len(self.peers))
                    peers = random.sample(self.peers, peer_num)
                    for peer in peers:
                        res = self.send_block(peer, self.current_block)
                        if res == -1:
                            self.peers.remove(peer)
                    break


    def handle_pending(self):
        self.pending_mutex.acquire()
        if len(self.pending_blocks) == 0:
            blk = None
        else:
            blk = self.pending_blocks.pop(0)
        self.pending_mutex.release()
        if blk == None:
            return

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

        # TODO: handle keyboard
        # signal.signal(signal.SIGINT, self.KeyboardInterruptHandler)

        # TODO: prepare and start RPC server

        self.loop(1, self.handle_update)
        self.loop(0.1, self.mine)
        self.loop(1, self.handle_pending)

        while not self.exit_flag:
            time.sleep(1)


if __name__ == "__main__":
    # service = Service()
    # service.start()

    p = Peer("127.0.0.1", 6379)
    print(p.get_bind())
