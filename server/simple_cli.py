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
    def trail_order(self):
        t = Prompt.ask("Type- Equity (e) Options (o) Futures (f)",choices=['e','o','f'],default='o')
        match t:
            case 'o':
                ci = Prompt.ask("Current Day Index",choices=['y','n'],default='y')
                if ci=='n':
                    i = Prompt.ask("Index- MidcapNifty(m) Finnifty(f) BankNifty(b) Nifty(n) Sensex(s)",choices=['m','f','b','n','s'])
                    date = Prompt.ask("Date")
                else:
                    i = ['m','f','b','n','s'][datetime.today().weekday()-1]
                    if i == 's':
                        #yet to do 
                        date = datetime.today().strftime("%y%d%b")    
                    date = datetime.today().strftime("%d%b%y")
                bscp = Prompt.ask("Buy/Sell Call/Put",choices=['bc','bp','sc','sp'])
                strike = Prompt.ask("Strike Price")
                trg = Prompt.ask("Trigger Price")
                q = Prompt.ask("Quantity (Lots)")
                pq = Prompt.ask("Partial Profit Booking Quantity Percent",choices=[25,50,75],default=50)
                match i:
                    case 'm':
                        lotsize = 50
                        instruname = f"MIDCPNIFTY{date.upper()}{bscp[1].upper()}{strike}"
                    case 'f':
                        lotsize = 25
                        instruname = f"FINNIFTY{date.upper()}{bscp[1].upper()}{strike}"
                    case 'b':
                        lotsize = 15
                        instruname = f"BANKNIFTY{date.upper()}{bscp[1].upper()}{strike}"
                    case 'n':
                        lotsize = 25
                        instruname = f"NIFTY{date.upper()}{bscp[1].upper()}{strike}"
                    case 's':
                        lotsize = 10
                        instruname = f"SENSEX{date.upper()}{strike}{bscp[1].upper()}E"
        if bscp[0] == 'b':
            r = requests.get(f"{serverurl}/to/{instruname}?bos=b&t={t}&q={lotsize*q}&fq={lotsize*(q*pq//100)}&p={trg+0.2}&tp={trg+0.05}&slp={trg-3-0.2}&sltp={trg-3-0.05}&fp={trg+2}")
        else:
            r = requests.get(f"{serverurl}/to/{instruname}?bos=s&t={t}&q={lotsize*q}&fq={lotsize*(q*pq//100)}&p={trg-0.2}&tp={trg-0.05}&slp={trg+3+0.2}&sltp={trg+3+0.05}&fp={trg-2}")
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
            case ['/to']:
                rq.trail_order()
            case ['/fnolist']:
                rq.fnolist()

            case _:
                pass
