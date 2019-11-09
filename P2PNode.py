#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import asyncio
import grpc
import P2PNode_pb2
import P2PNode_pb2_grpc

class P2PNode(P2PNode_pb2_grpc.P2PNodeServicer):
    def __init__(self):
        super(P2PNode, self).__init__()
        self.peers=0

    def setAddr(self,local_addr,peer_addr):
        self.local_addr=local_addr
        self.static_addr = peer_addr
    
    def SayHello(self, request, context):
        print("recive:",request.name)
        return P2PNode_pb2.HelloReply(message = 'hello {msg}'.format(msg = request.name))

    async def sendData(self):
        format_addr = "%s:%s" %(self.static_addr[0],self.static_addr[1])
        channel = grpc.insecure_channel(format_addr)
        stub = P2PNode_pb2_grpc.P2PNodeStub(channel)

        response = stub.SayHello(P2PNode_pb2.HelloRequest(name='czl'))
        print("response : " + response.message)
    #async def join(self,peer_addr):

     

