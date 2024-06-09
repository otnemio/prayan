from NorenRestApiPy.NorenApi import NorenApi
from logger import logger

class ShoonyaApiPy(NorenApi):
    
    feedOpen:bool
    log:logger
    
    def __init__(self):
        self.feedOpen = False
        self.log = logger()
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/')
    

    def event_handler_feed_update(self):
        pass
    
    def event_handler_order_update(self):
        pass

    def open_callback(self):
        self.feedOpen = True
        self.log.info('Feed is Open')

    def close_callback(self):
        self.feedOpen = False
        self.log.info('Feed is Close')