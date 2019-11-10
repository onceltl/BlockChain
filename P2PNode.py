#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import asyncio
import grpc
import P2PNode_pb2
import P2PNode_pb2_grpc
from concurrent import futures
from BlockChain import *

class P2PNode(object):
    def __init__(self):
        super(P2PNode, self).__init__()
        self.peers=0
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
        #self.table = KademiliaTable()
        #P2PNode_pb2_grpc.add_KademliaServicer_to_server(self.table, self.server)
        self.blockchain = BlockChain()
        P2PNode_pb2_grpc.add_BlockChainServicer_to_server(self.blockchain, self.server)

    def setAddr(self,local_addr,peer_addr):
        self.local_addr=local_addr
        self.static_addr = peer_addr

    def start(self):
        #gRPC
        format_addr = "%s:%s" %(self.local_addr[0],self.local_addr[1])
        self.server.add_insecure_port(format_addr)
        self.server.start()
    
    async def sendData(self):
        format_addr = "%s:%s" %(self.static_addr[0],self.static_addr[1])
        with grpc.insecure_channel(format_addr) as channel:
            stub = P2PNode_pb2_grpc.BlockChainStub(channel)
            response = stub.SayHello(P2PNode_pb2.HelloRequest(name='czl'))
            print("response : " + response.message)
    
    #async def join(self,peer_addr):


     

