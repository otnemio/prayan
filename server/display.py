import time
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from random import random

def generate_options_table():
    table = Table(title="Option Data")
    table.add_column("Call",width=6,justify="center")
    table.add_column("Strike",width=6,justify="right")
    table.add_column("Put",width=6,justify="right")

    
    table.add_row(f'{10+random():5.2f}','25700','154')
    table.add_row('20','25600','84')
    table.add_row('60','25500','54')
    table.add_row('80','25400','24')
    table.add_row('120','25300','15')

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

with Live(layout, refresh_per_second=1) as live:
    while True:
        tableOptions = generate_options_table()
        tableTrail = generate_trail_table()
        layout["upper"].update(Panel(Text("Dashboard",justify="center")))
        layout["left"].update(tableOptions)
        layout["right"].update(tableTrail)
        time.sleep(1)