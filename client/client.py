import readline, grpc, priyu_pb2, priyu_pb2_grpc
from rich.prompt import Prompt
from rich.console import Console

def command(stub:priyu_pb2_grpc.ChirperStub,msg):
    req = priyu_pb2.PRequest(msg=msg)
    res = stub.Command(req)
    con.print(res.msg)

if __name__ == '__main__':
    global con
    con = Console(stderr=False)
    stub = priyu_pb2_grpc.ChirperStub(grpc.insecure_channel('localhost:50051'))
    while True:
        cmd = Prompt.ask("₹")
        argLst = cmd.split(sep=' ')
        if argLst[0] == '':
            con.print('')
        if argLst[0] == '/?':
            command(stub,"Great")
