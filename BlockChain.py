#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import asyncio
import grpc
import P2PNode_pb2
import P2PNode_pb2_grpc
import block
import utils
import threading

class BlockChain(P2PNode_pb2_grpc.BlockChainServicer):
    def __init__(self):
        super(BlockChain, self).__init__()
        self.blocks = []
        self.mutex = threading.Lock()

    def get_block_num(self):
        return len(self.blocks)

    def add_block(self, blk):
        self.blocks.append(blk)

    def SayHello(self, request, context):
        print("recive:",request.name)
        print("context:", context)
        return P2PNode_pb2.HelloReply(message = 'hello {msg}'.format(msg = request.name))
    
    def GetBlockNum(self, request, context):
        block_num = len(self.blocks)
        return P2PNode_pb2.BlockNumReply(num = block_num)
    
    def GetBlock(self, request, context):
        try:
            with self.mutex:
                blk = self.blocks[idx]
            return P2PNode_pb2.BlockReply(blk = blk)
        except Exception:
            return P2PNode_pb2.BlockReply(blk = None)
        

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

    def SendBlock(self, request, context):
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

    def update_block(remote_head, remote_blocks):
        self.blocks = self.blocks[0:remote_head]
        rollback_num = len(remote_blocks)
        for i in range(rollback_num):
            self.blocks.append(remote_blocks[rollback_num - i - 1])
        print('update')