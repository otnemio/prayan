from NorenApi import NorenApi
from logger import logger
from sharedmethods import SharedMethods
import sqlite3, datetime, time, pandas as pd, yaml

class ShoonyaApi(NorenApi):
    
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/')
        self.feedOpen = False
        self.log = logger()
        self.connMem = sqlite3.connect(':memory:', check_same_thread=False)
        self.MD = {'orders':{},'cprice':{},'tradingsymbol':{},'liveTableExists':False, 'infoTableExists':False,
          'listtokens':[],'df_orders':None, 'df_holdings':None,'df_positions':None}
        

    def event_handler_feed_update(self,tick_data):
        if not self.feedOpen:
            return
        c = self.connMem.cursor()
        if tick_data['t']=='dk':
            self.MD['tradingsymbol'][tick_data['tk']]=tick_data['ts']
            c.execute('''CREATE TABLE IF NOT EXISTS info (
                        tradingsymbol TEXT,
                        ucp INTEGER,
                        lcp INTEGER,
                        PRIMARY KEY (tradingsymbol)
                            )''')
            c.execute('''INSERT OR IGNORE INTO info (tradingsymbol, ucp, lcp) VALUES (?,?,?)''',
                    (tick_data['ts'],SharedMethods.rp(tick_data['uc']),SharedMethods.rp(tick_data['lc'])))
            self.connMem.commit()
            self.MD['infoTableExists'] = True
        if tick_data['t']=='df' and not self.MD['liveTableExists'] and self.MD['infoTableExists']:    
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
            self.connMem.commit()
            self.MD['liveTableExists'] = True
            lastBusDay = datetime.datetime.today()
            lastBusDay = lastBusDay.replace(hour=0, minute=0, second=0, microsecond=0)
            
            for tkn in self.MD['listtokens']:
                exchange = tkn.split('|')[0]
                token = tkn.split('|')[1]
                ret = self.get_time_price_series(exchange=exchange, token=token, starttime=lastBusDay.timestamp(), interval=1)
                for row in ret:
                    if row['stat']=='Ok':
                        tm = datetime.datetime.strptime(row['time'],'%d-%m-%Y %H:%M:%S')
                        minute = SharedMethods.m0915(tm.hour,tm.minute)
                        c.execute('''INSERT OR IGNORE INTO live (tradingsymbol, minute, openp, highp, lowp, closep, volume) VALUES (?,?,?,?,?,?,?) ''',
                            (self.MD['tradingsymbol'][token],minute,
                            SharedMethods.rp(row['into']),
                            SharedMethods.rp(row['inth']),
                            SharedMethods.rp(row['intl']),
                            SharedMethods.rp(row['intc']),
                            int(row['intv'])))
            self.connMem.commit()
        if self.MD['liveTableExists'] and self.MD['infoTableExists'] and 'ft' in tick_data:    
            tm = time.localtime(int(tick_data['ft']))
            minute = SharedMethods.m0915(tm.tm_hour,tm.tm_min)
            tradingsymbol = self.MD['tradingsymbol'][tick_data['tk']]
            c.execute('''SELECT * FROM live WHERE tradingsymbol = ? AND minute = ?''',(tradingsymbol,minute,))
            row = c.fetchone()
            
            if 'lp' in tick_data:
                
                self.MD["cprice"][tradingsymbol]=float(tick_data['lp'])
                
                if not row:
                    c.execute('''INSERT OR IGNORE INTO live (tradingsymbol, minute, openp, highp, lowp, closep, volume) VALUES (?,?,?,?,?,?,?) ''',
                        (tradingsymbol,minute,
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
                    (nhighp,nlowp,nclosep,1,tradingsymbol,minute))
                self.connMem.commit()

    def event_handler_order_update(self,tick_data):
        if not self.feedOpen:
            return
        if self.MD['df_orders']['orderno'].str.contains(tick_data['norenordno']).any():
            self.MD['df_orders'].loc[self.MD['df_orders']['orderno']==tick_data['norenordno'],'status']=tick_data['status']
        else:
            self.MD['df_orders'].loc[self.MD['df_orders'].index.max()+1]=[tick_data['norenordno'],
                                                    tick_data['tsym'],
                                                    tick_data['qty'],
                                                    tick_data['prc'],
                                                    tick_data['status'],
                                                    tick_data['trantype']]
        if tick_data['status']=='COMPLETE':
            retp = self.get_positions()
            if retp:
                self.MD['df_positions'] = self.store_positions_data(retp)
            reto = self.get_order_book()
            if reto:
                self.MD['df_orders'] = self.store_orders_data(reto)
    
    def store_orders_data(self,data):
        df = {'orderno':[],'tradingsymbol':[],'quantity':[],'price':[],'status':[],'type':[],'ordertime':[]}
        for row in data:
            if row['stat']=='Ok':
                df['orderno'].append(row['norenordno'])
                df['tradingsymbol'].append(row['tsym'])
                df['quantity'].append(row['qty'])
                df['price'].append(row['prc'])
                df['status'].append(row['status'])
                df['type'].append(row['trantype'])
                df['ordertime'].append(row['norentm'])
        # log.info(df)
        return pd.DataFrame(df)

    def store_positions_data(self,data):
        df = {'tradingsymbol':[],'product':[],'quantity':[],'pnl':[]}
        for row in data:
            if row['stat']=='Ok':
                df['tradingsymbol'].append(row['tsym'])
                df['product'].append(row['s_prdt_ali'])
                df['quantity'].append(int(row['netqty']))
                df['pnl'].append(float(row['rpnl'])+float(row['urmtom']))
        return pd.DataFrame(df)

    
    def open_callback(self):
        self.feedOpen = True
        self.log.info('Feed is Open')
        with open("instruments.yaml","r") as stream:
            instruments = yaml.safe_load(stream)
            for instrument in instruments:
                for key, value in instrument.items():
                    for exch, token in value.items():
                        tradingsymbol = f"{key}-EQ" if exch =='NSE' else key
                        self.MD['listtokens'].append(f"{exch}|{token}|{tradingsymbol}")
        self.subscribe([i.rsplit('|', 1)[0] for i in self.MD['listtokens']],feed_type=2)

    def close_callback(self):
        self.feedOpen = False
        self.log.info('Feed is Close')
        self.connMem.close()

class Instrument():
    name:str
    exch:str
    tradename:str
    def __init__(self,name:str,exch:str='NSE') -> None:
        self.name = name.upper()
        self.exch = exch.upper()
        self.tradename =  name if self.exch !='NSE' else f'{name}-EQ'  
    
    
    