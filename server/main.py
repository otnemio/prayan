import sqlite3, os, yaml, logging, time, grpc, priyu_pb2, priyu_pb2_grpc
import pandas as pd
import threading
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from rich.logging import RichHandler
from concurrent import futures
from NorenRestApiPy.NorenApi import  NorenApi
from sharedmethods import SharedMethods

    
class Servicer(priyu_pb2_grpc.ChirperServicer):
    def __init__(self) -> None:
        super().__init__()
        self.ts = Timestamp()
    
    def Command(self, request, context):
        match request.msg:
            case 'session':
                return priyu_pb2.PReply(msg=MD["session"])
            case _:
                return priyu_pb2.PReply(msg=f"Good")
    def PosHold(self, request, context):
        quant = []
        match request.msg:
            case 'positions':
                if MD['df_positions'] is not None:
                    for index, row in MD['df_positions'].iterrows():
                        quant.append(priyu_pb2.Quant(tradingsymbol=row['tradingsymbol'],
                                                product=row['product'],
                                                pnl=row['pnl'],
                                                quantity=row['quantity']))
                return priyu_pb2.Quants(quant=quant)
            case 'holdings':
                if MD['df_holdings'] is not None:
                    for index, row in MD['df_holdings'].iterrows():
                        quant.append(priyu_pb2.Quant(tradingsymbol=row['tradingsymbol'],
                                                product=row['product'],
                                                quantity=row['quantity']))
                return priyu_pb2.Quants(quant=quant)
    def LiveData(self, request, context):
        tradingsymbol=f"{request.symbol}-EQ" if request.exchange=="NSE" else f"{request.symbol}"
        tohlcv = []
        if MD['liveTableExists']:
            c =conn_mem.cursor()
            c.execute('''SELECT * FROM live WHERE tradingsymbol = ?''',(tradingsymbol,))
            rows = c.fetchall()
            for row in rows:
                self.ts.FromDatetime(SharedMethods.tm0915(row[1]))
                tohlcv.append(priyu_pb2.OHLCV(time=self.ts,
                                              pOpen=row[2],
                                              pHigh=row[3],
                                              pClose=row[5],
                                              pLow=row[4],
                                              volume=row[6]))
        return priyu_pb2.OHLCVs(ohlcv=tohlcv)
            
    def BracketOrder(self, request, context):
        now = datetime.now()
        self.ts.FromDatetime(now)
        tradingsymbol=f"{request.symbol}-EQ"
        MD["orders"][now] = {'details':request,'positions':[],'targets':[],'stoploss':[]}
        
        return priyu_pb2.OrderReply(ordertime=self.ts)
    def ChildOrdersStatus(self, request, context):
        childorders = []
        for index, row in MD['df_orders'].iterrows():
            childorders.append(priyu_pb2.ChildOrder(orderno=row['orderno'],
                                                    tradingsymbol=row['tradingsymbol'],
                                                    status=row['status'],
                                                    type=priyu_pb2.Type.BUY if row['type']=='B' else priyu_pb2.Type.SELL,
                                                    quantity=int(row['quantity']),
                                                    p5Price=int(20*float(row['price']))))
        return priyu_pb2.ChildOrders(childorder=childorders)
    def AllOrdersStatus(self, request, context):
        try:
            orders = []
            for key, val in MD["orders"].items():
                # log.info(f"{key} {val}")
                self.ts.FromDatetime(key)
                children = []
                for child in val['positions']+val['stoploss']+val['targets']:
                    co = priyu_pb2.ChildOrder()
                    co.orderno = child[0]
                    co.status = child[1]
                    co.p5Price = int(20*child[2])
                    children.append(co)
                orders.append(priyu_pb2.Order(ordertime=self.ts,
                                              symbol=MD['orders'][key]['details'].symbol,
                                              p5Price=MD['orders'][key]['details'].p5Price,
                                              p5Target=MD['orders'][key]['details'].p5Target,
                                              p5StopLoss=MD['orders'][key]['details'].p5StopLoss,
                                              status=priyu_pb2.Status.COMPLETE,
                                              childorder=children))
            return priyu_pb2.Orders(order=orders)
        except Exception as e:
            log.error(e)

def initialize():
    global log, jobs, api, orders, MD
    jobs = []
    log = logging.getLogger("rich")
    
    MD = {'orders':{},'cprice':{},'tradingsymbol':{},'liveTableExists':False, 'infoTableExists':False, 'loggedin':False,
          'listtokens':[],'feedopened':False,'df_orders':None, 'df_holdings':None,'df_positions':None}
    api = ShoonyaApiPy()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    priyu_pb2_grpc.add_ChirperServicer_to_server(Servicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
    log.info("Server Started. Listening at [::]:50051")

def store_orders_data(data):
    df = {'orderno':[],'tradingsymbol':[],'quantity':[],'price':[],'status':[],'type':[]}
    for row in data:
        if row['stat']=='Ok':
            df['orderno'].append(row['norenordno'])
            df['tradingsymbol'].append(row['tsym'])
            df['quantity'].append(row['qty'])
            df['price'].append(row['prc'])
            df['status'].append(row['status'])
            df['type'].append(row['trantype'])
    # log.info(df)
    return pd.DataFrame(df)

def store_positions_data(data):
    df = {'tradingsymbol':[],'product':[],'quantity':[],'pnl':[]}
    for row in data:
        if row['stat']=='Ok':
            df['tradingsymbol'].append(row['tsym'])
            df['product'].append(row['s_prdt_ali'])
            df['quantity'].append(int(row['netqty']))
            df['pnl'].append(float(row['rpnl']))
    return pd.DataFrame(df)

def store_holdings_data(data):
    df = {'tradingsymbol':[],'product':[],'quantity':[]}
    for row in data:
        if row['stat']=='Ok':
            df['tradingsymbol'].append(row['exch_tsym'][0]['tsym'])
            df['product'].append(row['s_prdt_ali'])
            df['quantity'].append(max(int(row['dpqty']),int(row['npoadqty'])))
    return pd.DataFrame(df)

def shoonya(TOTP):
    api.fulllogin(TOTP)
    
    reth = api.get_holdings()
    if reth:
        MD['df_holdings'] = store_holdings_data(reth)
        log.info(MD['df_holdings'])
    
    retp = api.get_positions()
    if retp:
        MD['df_positions'] = store_positions_data(retp)
        log.info(MD['df_positions'])
    
    reto = api.get_order_book()
    if reto:
        MD['df_orders'] = store_orders_data(reto)
        log.info(MD['df_orders'])
    
    while True:
        for key, val in MD["orders"].items():
                # log.info(f"{key} {val}")
                # log.info(f"{MD['details'][key].symbol} {MD['details'][key].p5Price/20}")
                
                if MD["orders"][key]['positions']:
                    # log.info(MD["orders"][key])
                    for o in MD["orders"][key]:
                        pass
                        # ret = api.single_order_history(orderno=o)
                        # log.info(ret)
                else:
                    
                    MD["orders"][key]['positions'].append(('123456','complete',221.2))
                    MD["orders"][key]['positions'].append(('123457','open',221))
                    MD["orders"][key]['stoploss'].append(('324242','trigger_pending',220))
                                
                    # tradingsymbol = f"{MD['details'][key].symbol}-EQ"
                    # if abs (MD["details"][key].p5Price / 20.0 - MD["cprice"][tradingsymbol])<1.5:
                    #     price = (MD['details'][key].p5Price)/20.0
                    #     ord = api.place_order(buy_or_sell='B' if MD['details'][key].type==priyu_pb2.Type.BUY else 'S',
                    #                                 product_type='I', exchange='NSE',
                    #                                 tradingsymbol=f"{MD['details'][key].symbol}-EQ",
                    #                                 quantity=1, discloseqty=0, retention='DAY',
                    #                                 price_type='SL-LMT', price=price+0.15,
                    #                                 trigger_price=price+0.05,
                    #                                 remarks=f'{str(key)}')
                    #     if ord and ord['stat']=='Ok':
                    #         MD["orders"][key].append(ord['norenordno'])
                    #     # stop_loss = (MD['details'][key].p5Price-MD['details'][key].p5StopLoss)/20.0
                    #     # ord_s = api.place_order(buy_or_sell='S' if MD['details'][key].type==priyu_pb2.Type.BUY else 'B',
                    #     #                                 product_type='I', exchange='NSE',
                    #     #                                 tradingsymbol=f"{MD['details'][key].symbol}-EQ",
                    #     #                                 quantity=1, discloseqty=0, retention='DAY',
                    #     #                                 price_type='LMT', price=stop_loss-0.2,
                    #     #                                 trigger_price=stop_loss,
                    #     #                                 remarks=f'{str(key)}')
                    #     # if ord_s and ord_s['stat']=='Ok':
                    #     #         MD["orders"][key].append(ord_s['norenordno'])
                    #     target = (MD['details'][key].p5Price+MD['details'][key].p5Target)/20.0
                    #     ord_t = api.place_order(buy_or_sell='S' if MD['details'][key].type==priyu_pb2.Type.BUY else 'B',
                    #                                     product_type='I', exchange='NSE',
                    #                                     tradingsymbol=f"{MD['details'][key].symbol}-EQ",
                    #                                     quantity=1, discloseqty=0, retention='DAY',
                    #                                     price_type='LMT', price=target-0.2,
                    #                                     remarks=f'{str(key)}')
                    #     if ord_t and ord_t['stat']=='Ok':
                    #             MD["orders"][key].append(ord_t['norenordno'])
                    
        time.sleep(5)

class ShoonyaApiPy(NorenApi):
    
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/')
    
    def event_handler_feed_update(self,tick_data):
        if MD['feedopened']:
            c = conn_mem.cursor()
            if tick_data['t']=='dk':
                MD['tradingsymbol'][tick_data['tk']]=tick_data['ts']
                c.execute('''CREATE TABLE IF NOT EXISTS info (
                            tradingsymbol TEXT,
                            ucp INTEGER,
                            lcp INTEGER,
                            PRIMARY KEY (tradingsymbol)
                                )''')
                c.execute('''INSERT OR IGNORE INTO info (tradingsymbol, ucp, lcp) VALUES (?,?,?)''',
                        (tick_data['ts'],SharedMethods.rp(tick_data['uc']),SharedMethods.rp(tick_data['lc'])))
                conn_mem.commit()
                MD['infoTableExists'] = True
            if tick_data['t']=='df' and not MD['liveTableExists'] and MD['infoTableExists']:    
                c.execute('''CREATE TABLE IF NOT EXISTS live (
                        tradingsymbol TEXT,
                        minute INTEGER,
                        openp INTEGER,
                        highp INTEGER,
                        lowp INTEGER,
                        closep INTEGER,
                        volume INTEGER,
                        PRIMARY KEY (tradingsymbol,minute)
                        )''')
                conn_mem.commit()
                MD['liveTableExists'] = True
                lastBusDay = datetime.today()
                lastBusDay = lastBusDay.replace(hour=0, minute=0, second=0, microsecond=0)
                
                for tkn in MD['listtokens']:
                    exchange = tkn.split('|')[0]
                    token = tkn.split('|')[1]
                    ret = api.get_time_price_series(exchange=exchange, token=token, starttime=lastBusDay.timestamp())
                    for row in ret:
                        if row['stat']=='Ok':
                            tm = datetime.strptime(row['time'],'%d-%m-%Y %H:%M:%S')
                            minute = SharedMethods.m0915(tm.hour,tm.minute)
                            c.execute('''INSERT OR IGNORE INTO live (tradingsymbol, minute, openp, highp, lowp, closep, volume) VALUES (?,?,?,?,?,?,?) ''',
                                (MD['tradingsymbol'][token],minute,
                                SharedMethods.rp(row['into']),
                                SharedMethods.rp(row['inth']),
                                SharedMethods.rp(row['intl']),
                                SharedMethods.rp(row['intc']),
                                int(row['intv'])))
                conn_mem.commit()
            if MD['liveTableExists'] and MD['infoTableExists'] and 'ft' in tick_data:    
                tm = time.localtime(int(tick_data['ft']))
                minute = SharedMethods.m0915(tm.tm_hour,tm.tm_min)
                
                c.execute('''SELECT * FROM live WHERE tradingsymbol = ? AND minute = ?''',(MD['tradingsymbol'][tick_data['tk']],minute,))
                row = c.fetchone()
                
                if 'lp' in tick_data:
                    MD["cprice"][MD['tradingsymbol'][tick_data['tk']]]=float(tick_data['lp'])
                    if not row:
                        c.execute('''INSERT OR IGNORE INTO live (tradingsymbol, minute, openp, highp, lowp, closep, volume) VALUES (?,?,?,?,?,?,?) ''',
                            (MD['tradingsymbol'][tick_data['tk']],minute,
                             SharedMethods.rp(tick_data['lp']),
                             SharedMethods.rp(tick_data['lp']),
                             SharedMethods.rp(tick_data['lp']),
                             SharedMethods.rp(tick_data['lp']),
                             0))
                    else:        
                        nhighp = max(row[3],SharedMethods.rp(tick_data['lp']))
                        nlowp = min(row[4],SharedMethods.rp(tick_data['lp']))
                        nclosep = SharedMethods.rp(tick_data['lp'])
                        c.execute('''UPDATE live SET highp = ?, lowp = ?, closep =?, volume =? WHERE tradingsymbol = ? AND minute =?''',
                        (nhighp,nlowp,nclosep,1,MD['tradingsymbol'][tick_data['tk']],minute))
                    conn_mem.commit()

    def event_handler_order_update(self,tick_data):
        if MD['feedopened']:
            # log.info(f"order update {tick_data}")
            if MD['df_orders']['orderno'].str.contains(tick_data['norenordno']).any():
                MD['df_orders'].loc[MD['df_orders']['orderno']==tick_data['norenordno'],'status']=tick_data['status']
            else:
                MD['df_orders'].loc[MD['df_orders'].index.max()+1]=[tick_data['norenordno'],
                                                        tick_data['tsym'],
                                                        tick_data['qty'],
                                                        tick_data['prc'],
                                                        tick_data['status'],
                                                        tick_data['trantype']]
            if tick_data['status']=='COMPLETE':
                retp = api.get_positions()
                if retp:
                    MD['df_positions'] = store_positions_data(retp)

    def open_callback(self):
        global conn_mem
        MD['feedopened'] = True
        conn_mem = sqlite3.connect(':memory:',check_same_thread=False)

    def close_callback(self):
        MD['feedopened'] = False

    def fulllogin(self,TOTP):
        try:
            with open("cred.yaml","r") as stream:
                cred = yaml.safe_load(stream)
            if not MD['loggedin']:
                ret = self.login(cred['user'],cred['pwd'],TOTP,cred['vc'],cred['apikey'],cred['imei'])
                if not ret:
                    log.error("Problemia while trying to log in.")
                elif ret['stat']=='Ok':
                    MD["session"] = ret['susertoken']
                    MD['loggedin'] = True
                    self.start_websocket(order_update_callback=self.event_handler_order_update,
                        subscribe_callback=self.event_handler_feed_update, 
                        socket_open_callback=self.open_callback,
                        socket_close_callback=self.close_callback)
                    
                    with open("instruments.yaml","r") as stream:
                        instruments = yaml.safe_load(stream)
                        for instrument in instruments:
                            for key, value in instrument.items():
                                for exch, token in value.items():
                                    MD['listtokens'].append(f"{exch}|{token}")
                    self.subscribe(MD['listtokens'],feed_type=2)
                    
            log.info(f"Logged in: {MD['loggedin']}")
        except Exception as e:
                log.error(e)

if __name__ == '__main__':
    initialize()
    PIN = input("Auth Code ")
    t1 = threading.Thread(target=shoonya,args=(PIN,))
    t2 = threading.Thread(target=serve,args=())
    t1.start()
    t2.start()
    t1.join()
    t2.join()
