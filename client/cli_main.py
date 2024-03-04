import readline, grpc, priyu_pb2, priyu_pb2_grpc
from rich.prompt import Prompt
from rich.console import Console

class Requester():
    
    def __init__(self) -> None:
        self.stub = priyu_pb2_grpc.ChirperStub(grpc.insecure_channel('localhost:50051'))

    def command(self, msg):
        req = priyu_pb2.PRequest(msg=msg)
        res = self.stub.Command(req)
        con.print(res.msg)
    
    def bracketorder(self):
        req = priyu_pb2.OrderRequest(symbol='BEL',type=priyu_pb2.Type.BUY,
                                     p5Price=240*20,p5StopLoss=1*20,p5Target=2*20)
        res = self.stub.BracketOrder(req)
        con.print(res.ordertime)

    def allordersstatus(self):
        req = priyu_pb2.PRequest(msg='')
        res = self.stub.AllOrdersStatus(req)
        con.print(res)

if __name__ == '__main__':
    global con
    con = Console(stderr=False)
    rq = Requester()
    while True:
        cmd = Prompt.ask("\n₹")
        argLst = cmd.split(sep=' ')
        if argLst[0] == '/q':
            con.print('Bye')
            exit()
        if argLst[0] == '/?':
            rq.command("Great")
        if argLst[0] == '/os':
            rq.allordersstatus()
        if argLst[0] == '/bo':
            rq.bracketorder()
