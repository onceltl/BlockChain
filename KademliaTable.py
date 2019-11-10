#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import asyncio
import grpc
import P2PNode_pb2
import P2PNode_pb2_grpc

class Kademlia(P2PNode_pb2_grpc.KademliaServicer):
    def __init__(self,k,alpha):
        super(Kademlia, self).__init__()
    #def ping(peerId):

    #def pong(self, request, context):
