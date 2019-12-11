#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import asyncio
import grpc
import P2PNode_pb2
import P2PNode_pb2_grpc
import random
import traceback

class KademliaTable(P2PNode_pb2_grpc.KademliaServicer):
    
    def __init__(self,k=8,alpha=1,length=64):
        super(KademliaTable, self).__init__()
        self.k=k
        self.length=length
        self.alpha=alpha

        self.id = self.random_id()
        print("Kad_Id :",self.id)
        self.buckets = []
        for i in range(self.length+1):
            self.buckets.append([])

    def getNeighborhoods(self): #return list[ip,port]
        peers = []
        for bucket in self.buckets:
            for item in bucket:
                peers.append((item[0],item[1]))
        return peers
    
    #TODO regular_ping
    #TODO search_target
    def random_id(self):
        id=random.getrandbits(self.length)
        return id
    
    def add(self,ip,port,id):
        dis = self.distance(id,self.id)
        if dis == 0:
            return

        bucket = self.buckets[dis]
        for i in range(len(bucket)):
            if bucket[i][2] == id:
                del bucket[i]
                bucket.append((ip,port,id));
                return
        if len(bucket) < self.k :
            bucket.append((ip,port,id))
            print("add neighbor:",dis,ip,port,id)
        else:

            try:
                self.ping(bucket[0][0],bucket[0][1])
                item = bucket[0]
                del bucket[0]
                bucket.append(item)
            except Exception:
                traceback.print_exc()
                print("del neighbor:",dis,bucket[0][0],bucket[0][1],bucket[0][2])
                del bucket[0]
                bucket.append((ip,port,id))

                print("add neighbor:",dis,ip,port,id)
            
    def FindNode(self,addr,id):
        format_addr = "%s:%s" %(addr[0],addr[1])
        with grpc.insecure_channel(format_addr) as channel:
            stub = P2PNode_pb2_grpc.KademliaStub(channel)
            request = P2PNode_pb2.FindNodeRequest()
            request.sendAddr.ip = self.addr[0]
            request.sendAddr.port = self.addr[1]
            request.sendId=self.id
            request.targetId=id
            response = stub.reponseFindNode(request)
            return response
        return None

    def reponseFindNode(self, request, context):
        
        #add sendId
        self.add(request.sendAddr.ip,request.sendAddr.port,request.sendId)
        
        #query
        ansNode = [(self.distance(request.targetId,self.id),self.addr[0],self.addr[1],self.id)]

        for bucket in self.buckets:
            for item in bucket:
                ansNode.append((self.distance(request.targetId,item[2]),item[0],item[1],item[2]))
        ansNode.sort(key=lambda x:x[0])
        response = P2PNode_pb2.FindNodeReply()
        tot = 0
        for node in ansNode:
            nodeinfo = response.nodes.add()
            nodeinfo.addr.ip = node[1]
            nodeinfo.addr.port = node[2]
            nodeinfo.id = node[3]
            tot = tot +1
            if (tot > self.k): #can be more?
                break
        return response

    def ping(self,ip,port):
        #print("ping:",ip,port)
        format_addr = "%s:%s" %(ip,port)
        channel = grpc.insecure_channel(format_addr)
        stub = P2PNode_pb2_grpc.KademliaStub(channel)
        request = P2PNode_pb2.pingRequest()
        request.sendAddr.ip = self.addr[0]
        request.sendAddr.port = self.addr[1]
        request.message = "ping-pong"

        response = stub.pong(request)
        #print("ping right")

    def pong(self, request, context):
        #print("pong:",request.sendAddr,self.addr)
        return P2PNode_pb2.pongReply(message=request.message)


    def distance(self,ID,peerID):
        return (ID ^ peerID).bit_length()

    def setAddr(self,addr):
        self.addr=addr

    def join(self,static_addr):
        peers = [static_addr]
        used = set()
        used.add(self.id)
        while len(peers) > 0 : # can be limit times
            response = self.FindNode(peers[0],self.id)
            #print("-------------",peers[0]);
            del peers[0]
            #print(response)
            for node in response.nodes:
                if node.id not in used :
                    if (node.addr.ip,node.addr.port)!=static_addr:
                        peers.append((node.addr.ip,node.addr.port))
                    used.add(node.id)
                    self.add(node.addr.ip,node.addr.port,node.id)



if __name__ == '__main__':
    #unit test
    a=KademliaTable()
    a.setAddr(("10.0.0.1",50000))
    request = P2PNode_pb2.FindNodeRequest()
    request.sendAddr.ip = "10.0.0.2"
    request.sendAddr.port = 50000
    request.sendId=a.random_id()
    request.targetId=request.sendId
    a.reponseFindNode(request,1)
