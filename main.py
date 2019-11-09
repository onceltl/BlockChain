#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import asyncio
import sys
from concurrent import futures
from P2PNode import *

node =None;

async def dealCMD(line):
    line = line.split();
    global node
    if line[0]=="sendData":
        await node.sendData()
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

    #gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    P2PNode_pb2_grpc.add_P2PNodeServicer_to_server(node, server)

    format_addr = "%s:%s" %(local_addr[0],local_addr[1])
    server.add_insecure_port(format_addr)
    server.start()




    tasks = [
        asyncio.ensure_future(monitorCommand()),
    ]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    
if __name__ == '__main__':
    local_addr=(sys.argv[1], int(sys.argv[2]))
    peer_addr=(sys.argv[3], int(sys.argv[4]))
    mode  = (sys.argv[5])
    print("local_addr:",local_addr)
    print("static_addr:",peer_addr)
    print("mode:",mode)
    setUpEvent(local_addr,peer_addr,mode);