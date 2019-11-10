#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import asyncio
import grpc
import P2PNode_pb2
import P2PNode_pb2_grpc

class BlockChain(P2PNode_pb2_grpc.BlockChainServicer):
    def __init__(self):
        super(BlockChain, self).__init__()

    def SayHello(self, request, context):
        print("recive:",request.name)
        return P2PNode_pb2.HelloReply(message = 'hello {msg}'.format(msg = request.name))
    #TODO