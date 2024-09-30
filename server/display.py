import time
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from random import random
from rich.prompt import Prompt
import requests
from sharedmethods import SM

def generate_options_table():
    r = requests.get(f"{serverurl}/s/MIDCPNIFTY")
    if r.status_code == 200:
        d = r.json()['Msg']
        table = Table(title=f"Option Data {d['Instrument']}")
        table.add_column("Call",width=6,justify="center")
        table.add_column("Strike",width=6,justify="right")
        table.add_column("Put",width=6,justify="right")

        for key,val in d['OptionDataCP'].items():
            table.add_row(f"{val[0] if val[0] is not None else 0:>6.2f}",f"{key}",f"{val[1] if val[1] is not None else 0:>6.2f}")

    return table

def generate_trail_table():
    table = Table(title="Trail Orders")
    table.add_column("Instrument & Price")

    t1 = Tree(f'NFT 25650 [green]{23.70:>6.2f}')
    t1.add(f'Frwrd [red]{25.55:>6.2f}')
    t1.add(f'StpLs [yellow]{20.85:>6.2f}')
    table.add_row(f'NFT 25600 [yellow]{12.25:>6.2f}')
    table.add_row(t1)
    table.add_row(f'BNF 52500 [yellow]{85.35:>6.2f}')
    table.add_row(f'MDC 13400 [yellow]{78.30:>6.2f}')
    table.add_row(f'FNF 24300 [yellow]{100.25:>6.2f}')

    return table

layout = Layout()
layout.split_column(
    Layout(name="upper", size=3),
    Layout(name="lower"),
)
layout["lower"].split_row(
    Layout(name="left"),
    Layout(name="right"),
)

def initialize():
    global serverurl
    port = Prompt.ask('Enter port',default='8081')
    serverurl = f'http://localhost:{port}'
    print(f'Server is {serverurl}')
    r = requests.get(f"{serverurl}")
    if r.status_code == 200:
        print(r.json()['Msg'])

initialize()
with Live(layout, refresh_per_second=1) as live:
    while True:
        tableOptions = generate_options_table()
        tableTrail = generate_trail_table()
        layout["upper"].update(Panel(Text("Dashboard",justify="center")))
        layout["left"].update(tableOptions)
        layout["right"].update(tableTrail)
        time.sleep(1)