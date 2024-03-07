import os, yaml, logging, time, grpc, priyu_pb2, priyu_pb2_grpc
import pandas as pd
import threading
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from rich.logging import RichHandler
from concurrent import futures
from NorenRestApiPy.NorenApi import  NorenApi

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
    
    def BracketOrder(self, request, context):
        now = datetime.now()
        self.ts.FromDatetime(now)
        tradingsymbol=f"{request.symbol}-EQ"
        MD["orders"][now] = []
        MD["details"][now] = request
        
        return priyu_pb2.OrderReply(ordertime=self.ts)
    
    def AllOrdersStatus(self, request, context):
        try:
            orders = []
            for key, val in MD["orders"].items():
                # log.info(f"{key} {val}")
                self.ts.FromDatetime(key)
                children = []
                for child in val:
                    co = priyu_pb2.ChildOrder()
                    co.orderno = child[0]
                    co.status = child[1]
                    co.p5Price = int(20*child[2])
                    children.append(co)
                orders.append(priyu_pb2.Order(ordertime=self.ts,
                                              symbol=MD['details'][key].symbol,
                                              status=priyu_pb2.Status.COMPLETE,
                                              childorder=children))
            return priyu_pb2.Orders(order=orders)
        except Exception as e:
            log.error(e)

def initialize():
    global log, jobs, api, orders, MD
    jobs = []
    log = logging.getLogger("rich")
    
    MD = {'orders':{},'details':{},'cprice':{}}
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
    df = {'orderno':[],'symbol':[],'price':[],'status':[]}
    for row in data:
        if row['stat']=='Ok':
            df['orderno'].append(row['norenordno'])
            df['symbol'].append(row['tsym'])
            df['price'].append(row['prc'])
            df['status'].append(row['status'])
    df_orders = pd.DataFrame(df)
    log.info(df_orders)
def shoonya(TOTP):
    api.fulllogin(TOTP)
    ret = api.get_order_book()
    store_orders_data(ret)
    while True:
        for key, val in MD["orders"].items():
                # log.info(f"{key} {val}")
                # log.info(f"{MD['details'][key].symbol} {MD['details'][key].p5Price/20}")
                
                if MD["orders"][key]:
                    # log.info(MD["orders"][key])
                    for o in MD["orders"][key]:
                        pass
                        # ret = api.single_order_history(orderno=o)
                        # log.info(ret)
                else:
                    
                    MD["orders"][key].append(('123456','open',221.2))
                    MD["orders"][key].append(('324242','complete',220))
                                
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
        self.feed_opened = False
        self.loggedin = False
        self.list_tokens = []
        self.symbol = {}
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/')
    
    def event_handler_feed_update(self,tick_data):
        if self.feed_opened:
            if tick_data['t']=='dk':
                self.symbol[tick_data['tk']]=tick_data['ts']
            if 'lp' in tick_data:
                MD["cprice"][self.symbol[tick_data['tk']]]=float(tick_data['lp'])
            pass

    def event_handler_order_update(self,tick_data):
        if self.feed_opened:
            log.info(f"order update {tick_data}")
            NS.df_orders = [1]
            pass

    def open_callback(self):
        self.feed_opened = True

    def close_callback(self):
        self.feed_opened = False

    def fulllogin(self,TOTP):
        try:
            with open("cred.yaml","r") as stream:
                cred = yaml.safe_load(stream)
            if not self.loggedin:
                ret = self.login(cred['user'],cred['pwd'],TOTP,cred['vc'],cred['apikey'],cred['imei'])
                if not ret:
                    log.error("Problemia while trying to log in.")
                elif ret['stat']=='Ok':
                    MD["session"] = ret['susertoken']
                    self.loggedin = True
                    self.start_websocket(order_update_callback=self.event_handler_order_update,
                        subscribe_callback=self.event_handler_feed_update, 
                        socket_open_callback=self.open_callback,
                        socket_close_callback=self.close_callback)
                    
                    with open("instruments.yaml","r") as stream:
                        instruments = yaml.safe_load(stream)
                        for instrument in instruments:
                            for key, value in instrument.items():
                                for exch, token in value.items():
                                    self.list_tokens.append(f"{exch}|{token}")
                    self.subscribe(self.list_tokens,feed_type=2)
                    
            log.info(f"Logged in: {self.loggedin}")
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
