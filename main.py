#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import asyncio
import sys
from P2PNode import *

#node =None

import time
import signal
import random
import threading

import block
import utils
import crypto


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
        self.local_peer = None
        self.peers = []
        self.peer_num = 6

        # Transaction
        self.key_private = crypto.gen_key_private()
        self.key_public = crypto.gen_key_public(self.key_private)
        self.addr = crypto.gen_addr(self.key_public)
        self.transaction_mutex = asyncio.Lock()
        self.pending_transactions = []

        # Mine
        self.ver = 0
        self.transaction_max_num = 10
        self.thresh = 10
        self.fee = 1024

        # Local blocks
        self.mutex = asyncio.Lock()
        self.blocks = []

        # Pending blocks
        self.pending_mutex = asyncio.Lock()
        self.pending_blocks = []
        self.current_block = None

        self.node = None




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
        blk = self.node.get_block(peer, idx)

        blk = block.Block()
        self.valid_block(blk)
        return blk
    


    def send_block(self, peer, blk):

        self.node.send_block(peer, blk)
        # TODO: send block to peer
        return -1


    async def handle_update(self):
        while True:
            await asyncio.sleep(1) 
            await self.setNeighborhood()            
            #if True:
            with await self.mutex:
                len_local = self.node.get_block_num(self.local_peer)
                peer_num = min(self.peer_num, len(self.peers))
                peers = random.sample(self.peers, peer_num)
                candidates = []
                for peer in peers:
                    len_remote = self.node.get_block_num(peer)
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
                    local_tail = len_local - 1
                    remote_head = len_local
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
                    self.node.update_block(remote_head, remote_blocks)
                

                    '''self.blocks = self.blocks[0:remote_head]
                    rollback_num = len(remote_blocks)
                    for i in range(rollback_num):
                        self.blocks.append(remote_blocks[rollback_num - i - 1])'''


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
    async def mine(self):
        while True:
            await asyncio.sleep(0.1) 
            await self.setNeighborhood()
            with await self.mutex:
                self.update_current_block()
                times = 2 ** (self.thresh - 1)
                for _ in range(times):
                    nonce = int(random.random() * pow(2, 64))
                    self.current_block.set_nonce(nonce)
                    if self.valid_block(self.current_block):
                        self.node.send_block(self.local_peer, self.current_block)
                        #self.blocks.append(self.current_block)
                        peer_num = min(self.peer_num, len(self.peers))
                        peers = random.sample(self.peers, peer_num)
                        for peer in peers:
                            res = self.send_block(peer, self.current_block)
                            #if res == -1:
                                #self.peers.remove(peer)
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
    
    def setUpEvent(self, local_addr,peer_addr,mode):

        self.node = P2PNode()
        self.node.setAddr(local_addr,peer_addr)
        self.node.start()
        

        tasks = [
            asyncio.ensure_future(self.monitorCommand()),
            asyncio.ensure_future(self.setNeighborhood()),
            asyncio.ensure_future(self.handle_update()),
            asyncio.ensure_future(self.mine()),
            #asyncio.ensure_future(self.blockMonitor(p)),
        ]

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    async def setNeighborhood(self):
        with await self.mutex:
            p = Peer(local_addr[0], local_addr[1])
            self.local_peer = p
            neighbor = await self.node.getNeighborhoods()
            for node in neighbor:
                if Peer(node[0], node[1]) not in self.peers:
                    self.peers.append(Peer(node[0], node[1]))

    async def blockMonitor(self, p):
        while True:
            await asyncio.sleep(1)
            
    
    async def dealCMD(self, line):
        line = line.split()
        if line[0]=="sendData":
            await self.node.sendData()
        elif line[0] == "showRoutTable":
            await self.node.printRoutTable()
        #TODO
        elif line[0] == "runCMDFromFile":
            pass
        elif line[0] == "createTX":
            pass
        elif line[0] == "CheckBalances":
            pass 
        else:
            print("pass cmd :",line[0])
            pass 

    async def monitorCommand(self):
        while True:
            loop = asyncio.get_event_loop()
            line = await loop.run_in_executor(None, sys.stdin.readline)
            line = line.strip()
            if not line:
                continue
            print('Got line:', line)
            await self.dealCMD(line)
            
    def start(self, local_addr, peer_addr, mode):
        self.setUpEvent(local_addr,peer_addr,mode)

        #self.loop(1, self.handle_update)
        #self.loop(0.1, self.mine)
        #self.loop(1, self.handle_pending)

        #while not self.exit_flag:
        #    time.sleep(1)

'''
async def dealCMD(line):
    line = line.split()
    global node
    if line[0]=="sendData":
        await node.sendData()
    elif line[0] == "showRoutTable":
        await node.printRoutTable()
    #TODO
    elif line[0] == "runCMDFromFile":
        pass
    elif line[0] == "createTX":
        pass
    elif line[0] == "CheckBalances":
        pass 
    else:
        print("pass cmd :",line[0]);
        pass 

async def monitorCommand():
    while True:
        loop = asyncio.get_event_loop()
        line = await loop.run_in_executor(None, sys.stdin.readline)
        line = line.strip()
        if not line:
           continue;
        print('Got line:', line)
        await dealCMD(line)
    
def setUpEvent(local_addr,peer_addr,mode):

    global node
    node=P2PNode();
    node.setAddr(local_addr,peer_addr);
    node.start();
    
    tasks = [
        asyncio.ensure_future(monitorCommand()),
    ]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
'''    
if __name__ == '__main__':
    local_addr = (sys.argv[1], int(sys.argv[2]))
    peer_addr = (sys.argv[3], int(sys.argv[4]))
    mode = (sys.argv[5])
    print("local_addr:",local_addr)
    print("static_addr:",peer_addr)
    print("mode:",mode)
    service = Service()
    service.start(local_addr, peer_addr, mode)
    #setUpEvent(local_addr,peer_addr,mode);