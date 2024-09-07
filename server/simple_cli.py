import readline, yaml, os
from datetime import datetime, timezone
from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from rich.pretty import pprint
import requests

class Requester():
    
    def __init__(self) -> None:
        global serverurl
        port = Prompt.ask('Enter port',default='8081')
        serverurl = f'http://localhost:{port}'
        print(f'Server is {serverurl}')
        r = requests.get(f"{serverurl}")
        if r.status_code == 200:
            print(r.json()['Msg'])
    def login(self,TOTP):
        r = requests.get(f"{serverurl}/login?totp={TOTP}")
        if r.status_code == 200:
            print(r.json()['Msg'])
    def orders(self):
        r = requests.get(f"{serverurl}/orders")
        if r.status_code == 200:
            print(r.json()['Msg'])
    def fnolist(self):
        r = requests.get(f"{serverurl}/fnolist")
        if r.status_code == 200:
            table = Table(title=f"FnO list with lot sizes", box=box.HORIZONTALS)

            table.add_column("Symbol", justify="lest", style="medium_purple3")
            table.add_column("Lot size", justify="right", style="light_steel_blue1")
            
            for item in r.json():
                table.add_row(item['Symbol'],item['Lot Size (Sep\xa02024)'])
            
            con.print(table)
    def allordersstatus(self):
        res = requests.get("http://localhost:8080/")
        table = Table(title=f"FnO list with lot sizes", box=box.HORIZONTALS)

        table.add_column("Instrument", justify="center", style="medium_purple3")
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
        cmd = Prompt.ask("\n₹")
        match cmd.split():
            case ['/q']:
                con.print('Bye')
                exit()
            case ['/l',TOTP]:
                rq.login(TOTP)
            case ['/os']:
                rq.orders()
            case ['/fnolist']:
                rq.fnolist()

            case _:
                pass
