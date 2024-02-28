import logging, time
from rich.logging import RichHandler
import multiprocessing as mp

def initialize():
    global log, jobs
    jobs = []
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )
    log = logging.getLogger("rich")

def shoonya(PIN):
    while True:
        log.info("Hello, World!")
        time.sleep(5)

if __name__ == '__main__':
    initialize()
    PIN = input("Auth Code ")
    with mp.Pool() as pool:
        jobs.append(pool.apply_async(shoonya, [PIN]))
        # jobs.append(pool.apply_async(analyser, []))
        
        while True:
            pass
