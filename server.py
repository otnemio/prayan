import logging, time, grpc, priyu_pb2, priyu_pb2_grpc
from rich.logging import RichHandler
import multiprocessing as mp
from concurrent import futures

class Servicer(priyu_pb2_grpc.ChirperServicer):
    
    def Command(self, request, context):
        log.info("Good, World!")
        return priyu_pb2.PReply(msg=f"Good")

def initialize():
    global log, jobs
    jobs = []
    log = logging.getLogger("rich")

    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    priyu_pb2_grpc.add_ChirperServicer_to_server(Servicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
    log.info("Server Started. Listening at [::]:50051")

def shoonya(PIN):    
    while True:
        log.info("Hello, World!")
        time.sleep(5)

if __name__ == '__main__':
    initialize()
    PIN = input("Auth Code ")
    with mp.Pool() as pool:
        jobs.append(pool.apply_async(shoonya, [PIN]))
        jobs.append(pool.apply_async(serve, []))
        # jobs.append(pool.apply_async(analyser, []))
        
        while True:
            pass
