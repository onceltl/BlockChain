#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import asyncio
import grpc
import P2PNode_pb2
import P2PNode_pb2_grpc
from concurrent import futures
from BlockChain import *
from KademliaTable import * 
class P2PNode(object):
    def __init__(self, ser):
        super(P2PNode, self).__init__()
        self.peers=0
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
        self.table = KademliaTable()
        P2PNode_pb2_grpc.add_KademliaServicer_to_server(self.table, self.server)
        # self.blockchain = BlockChain()
        P2PNode_pb2_grpc.add_BlockChainServicer_to_server(ser, self.server)

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

    async def sendData(self):
        format_addr = "%s:%s" %(self.static_addr[0],self.static_addr[1])
        with grpc.insecure_channel(format_addr) as channel:
            stub = P2PNode_pb2_grpc.BlockChainStub(channel)
            response = stub.SayHello(P2PNode_pb2.HelloRequest(name='czl'))
            print("response : " + response.message)

    

    def get_block_num(self, node):
        format_addr = "%s:%s" %(node[0],node[1])
        with grpc.insecure_channel(format_addr) as channel:
            stub = P2PNode_pb2_grpc.BlockChainStub(channel)
            response = stub.GetBlockNum(P2PNode_pb2.BlockNumRequest())
            return response.num

    
    
    def get_block(self, node, idx):
        format_addr = "%s:%s" %(node[0],node[1])
        with grpc.insecure_channel(format_addr) as channel:
            stub = P2PNode_pb2_grpc.BlockChainStub(channel)
            response = stub.GetBlock(P2PNode_pb2.GetBlockRequest(idx=idx))

            return response.blk

    def send_block(self, node, blk):
        format_addr = "%s:%s" %(node[0],node[1])
        with grpc.insecure_channel(format_addr) as channel:
            stub = P2PNode_pb2_grpc.BlockChainStub(channel)
            response = stub.SendBlock(P2PNode_pb2.SendBlockRequest(blk=blk))

            return 
 
    def send_pre_and_new_hash(self, node, blk1, blk2):
        format_addr = "%s:%s" %(node[0],node[1])
        with grpc.insecure_channel(format_addr) as channel:
            stub = P2PNode_pb2_grpc.BlockChainStub(channel)
            response = stub.SendPreAndNewHash(P2PNode_pb2.SendPreAndNewHashRequest(blk1 = blk1, blk2 = blk2))
            return

     

