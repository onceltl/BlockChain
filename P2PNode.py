#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import asyncio
import grpc
import block
import P2PNode_pb2
import P2PNode_pb2_grpc
from concurrent import futures
from BlockChain import *
from KademliaTable import * 
class P2PNode(object):
    def __init__(self):
        super(P2PNode, self).__init__()
        self.peers=0
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
        self.table = KademliaTable()
        P2PNode_pb2_grpc.add_KademliaServicer_to_server(self.table, self.server)
        self.blockchain = BlockChain()
        P2PNode_pb2_grpc.add_BlockChainServicer_to_server(self.blockchain, self.server)

    def setAddr(self,local_addr,peer_addr):
        self.local_addr=local_addr
        self.static_addr = peer_addr
        self.table.setAddr(local_addr)
    
    def start(self):
        #gRPC 
        format_addr = "%s:%s" %(self.local_addr[0],self.local_addr[1])
        self.server.add_insecure_port(format_addr)
        self.server.start()
        if self.local_addr!=self.static_addr:
            self.table.join(self.static_addr)
    
    async def printRoutTable(self):
        print(self.table.getNeighborhoods())

    async def getNeighborhoods(self):
        return self.table.getNeighborhoods()

    def send_block(peer, blk):
        if peer.host == self.local_addr[0] and peer.port == self.local_addr[1]:
            self.blockchain.addblk(blk)
        else:
            for node in self.table.getNeighborhoods():
                if peer.host == node[0] and peer.port == node[1]:
                    format_addr = "%s:%s" %(node[0],node[1])
                    with grpc.insecure_channel(format_addr) as channel:
                        stub = P2PNode_pb2_grpc.BlockChainStub(channel)
                        stub.GetBlock(P2PNode_pb2.SendBlock(blk=blk))
                        

    def get_block(self, peer, idx):
        if peer.host == self.local_addr[0] and peer.port == self.local_addr[1]:
            return self.blockchain.get_block(idx)
        else:
            for node in self.table.getNeighborhoods():
                if peer.host == node[0] and peer.port == node[1]:
                    format_addr = "%s:%s" %(node[0],node[1])
                    with grpc.insecure_channel(format_addr) as channel:
                        stub = P2PNode_pb2_grpc.BlockChainStub(channel)
                        response = stub.GetBlock(P2PNode_pb2.BlockNumRequest(idx=idx))
                        return response.blk
            print("response : ", -1)
            return None

    def get_block_num(self, peer):
        if peer.host == self.local_addr[0] and peer.port == self.local_addr[1]:
            return self.blockchain.get_block_num()
        else:
            for node in self.table.getNeighborhoods():
                if peer.host == node[0] and peer.port == node[1]:
                    format_addr = "%s:%s" %(node[0],node[1])
                    with grpc.insecure_channel(format_addr) as channel:
                        stub = P2PNode_pb2_grpc.BlockChainStub(channel)
                        response = stub.GetBlockNum(P2PNode_pb2.BlockNumRequest())
                        return response.num
            return -1

    def update_block(remote_head, remote_blocks):
        self.blockchain.update_block(remote_head, remote_blocks)

    async def sendData(self):
        for node in self.table.getNeighborhoods():
            format_addr = "%s:%s" %(node[0],node[1])
            with grpc.insecure_channel(format_addr) as channel:
                stub = P2PNode_pb2_grpc.BlockChainStub(channel)
                response = stub.SayHello(P2PNode_pb2.HelloRequest(name='czl'))
                print("response : " + response.message)
    


     

