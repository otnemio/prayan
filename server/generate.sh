python3 -m grpc_tools.protoc -I=./protos --python_out=. --grpc_python_out=. ./protos/*.proto
cp *_pb2*.py ../client