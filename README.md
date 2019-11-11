# BlockChain
BlockChain simulation

## Dependencies 
- Mininet2.3.0d5(http://mininet.org/ , 最好先将系统的默认python版本调整为python3,然后选择2.3.0版本编译安装)
- gRPC (https://grpc.github.io/grpc/python/grpc.html#module-contents  https://grpc.github.io/grpc/python/grpc.html#module-contents)

## How to Run
- 首先用 ` ` `python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I. P2PNode.proto` ` ` 生成gRPC文件
- 然后用` ` `python setP2PNet.py` ` `启动mininet模拟器
- mininet模拟器启动后会为每个网络节点分配一个终端，并自动运行程序` ` `main.py` ` `(可以通过终端交互)
