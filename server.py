import os, yaml, logging, time, grpc, priyu_pb2, priyu_pb2_grpc
from rich.logging import RichHandler
import multiprocessing as mp
from concurrent import futures
from NorenRestApiPy.NorenApi import  NorenApi

class Servicer(priyu_pb2_grpc.ChirperServicer):
    
    def Command(self, request, context):
        log.info("Good, World!")
        return priyu_pb2.PReply(msg=f"Good")

def initialize():
    global log, jobs, api
    jobs = []
    log = logging.getLogger("rich")
    api = None
    # abspath = os.path.abspath(__file__)
    # dname = os.path.dirname(abspath)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    priyu_pb2_grpc.add_ChirperServicer_to_server(Servicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
    log.info("Server Started. Listening at [::]:50051")

def shoonya(TOTP):
    api = ShoonyaApiPy()
    api.fulllogin(TOTP)
    while True:
        log.info("Hello, World!")
        time.sleep(15)

class ShoonyaApiPy(NorenApi):
    
    def __init__(self):
        self.feed_opened = False
        self.loggedin = False
        self.list_tokens = []
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        
        # api = self
    
    def event_handler_feed_update(self,tick_data):
        if self.feed_opened:
            log.info(f"feed update {tick_data}")

    def event_handler_order_update(self,tick_data):
        if self.feed_opened:
            log.info(f"order update {tick_data}")

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
    with mp.Pool() as pool:
        jobs.append(pool.apply_async(shoonya, [PIN]))
        jobs.append(pool.apply_async(serve, []))
        # jobs.append(pool.apply_async(analyser, []))
        
        while True:
            pass
