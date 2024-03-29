import readline, yaml, os, grpc, priyu_pb2, priyu_pb2_grpc
from datetime import datetime, timezone
from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table
from rich import box
from NorenRestApiPy.NorenApi import  NorenApi

class Requester():
    
    def __init__(self) -> None:
        self.stub = priyu_pb2_grpc.ChirperStub(grpc.insecure_channel('localhost:50051'))

    def command(self, msg):
        req = priyu_pb2.PRequest(msg=msg)
        res = self.stub.Command(req)
        return res.msg
    
    def bracketorder(self, price):
        req = priyu_pb2.OrderRequest(symbol='BHEL',type=priyu_pb2.Type.BUY,
                                     p5Price=int(float(price)*20),p5StopLoss=1*20,p5Target=2*20)
        res = self.stub.BracketOrder(req)
        con.print(res.ordertime)

    def childordersstatus(self):
        req = priyu_pb2.PRequest(msg='')
        res = self.stub.ChildOrdersStatus(req)
        table = Table(title=f"Child Orders", box=box.HORIZONTALS)

        table.add_column("Order Number", justify="center", style="medium_purple3")
        table.add_column("Trading Symbol", justify="center", style="light_steel_blue1")
        table.add_column("Type", justify="center", style="light_steel_blue1")
        table.add_column("Status", justify="center", style="light_steel_blue1")
        table.add_column("Quantity", justify="right", style="cyan")
        table.add_column("Price", justify="right", style="cyan")

        for childorder in res.childorder:
            table.add_row(f"{childorder.orderno:15}",f"{childorder.tradingsymbol:15}",f"{priyu_pb2.Type.Name(childorder.type)}",
                          f"{childorder.status}",f"{childorder.quantity}",
                          f"{childorder.p5Price/20:>8.2f}")
        
        con.print(table)
    def livedata(self):
        req = priyu_pb2.SRequest(symbol='BEL',exchange='NSE')
        res = self.stub.LiveData(req)
        table = Table(title=f"Live Data (BEL)", box=box.HORIZONTALS)

        table.add_column("Time", justify="center", style="medium_purple3")
        table.add_column("Open", justify="right", style="light_steel_blue1")
        table.add_column("High", justify="right", style="light_steel_blue1")
        table.add_column("Low", justify="right", style="light_steel_blue1")
        table.add_column("Close", justify="right", style="light_steel_blue1")
        table.add_column("Volume", justify="right", style="cyan")
        con.print(res)
        

    def allordersstatus(self):
        req = priyu_pb2.PRequest(msg='')
        res = self.stub.AllOrdersStatus(req)
        table = Table(title=f"All Orders", box=box.HORIZONTALS)

        table.add_column("Order Time", justify="center", style="medium_purple3")
        table.add_column("Symbol", justify="center", style="light_steel_blue1")
        table.add_column("StopLoss", justify="right", style="cyan")
        table.add_column("Price", justify="right", style="cyan")
        table.add_column("Target", justify="right", style="cyan")
        table.add_column("Child Order", justify="right", style="dark_orange3")
        table.add_column("Status", justify="left", style="dark_orange3")

        for order in res.order:
            table.add_row(f"{datetime.fromtimestamp(order.ordertime.seconds,tz=timezone.utc).strftime('%H:%M:%S')}",
                        f"{order.symbol:10}",f"{order.p5StopLoss/20:>8.2f}",f"{order.p5Price/20:>8.2f}",f"{order.p5Target/20:>8.2f}",
                        "")
            for child in order.childorder:
                table.add_row("","","","","",child.orderno,child.status)
                # con.print(api.single_order_history(child))
            
        con.print(table)

def initialize():
    global con, rq
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    con = Console(stderr=False)
    rq = Requester()
    
    
if __name__ == '__main__':
    initialize()
    while True:
        cmd = Prompt.ask("₹")
        match cmd.split():
            case ['/q']:
                con.print('Bye')
                exit()
            case ['/os']:
                rq.allordersstatus()
            case ['/cs']:
                rq.childordersstatus()
            case ['/l']:
                rq.livedata()
            case ['/o']:
                rq.command('session')
            case ['/bo',price]:
                rq.bracketorder(price)

            case _:
                # con.print("Sorry")
                pass
