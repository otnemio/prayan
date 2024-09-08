from NorenRestApiPy.NorenApi import NorenApi
from logger import logger
from sharedmethods import SharedMethods
import sqlite3, datetime, time, pandas as pd, yaml

class ShoonyaApi(NorenApi):
    
    def __init__(self,TOTP,aftermarket):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                          websocket='wss://api.shoonya.com/NorenWSTP/')
        self.feedOpen = False
        self.log = logger()
        self.connMem = sqlite3.connect(':memory:', check_same_thread=False)
        self.MD = {'orders':{},'ltp':{},'tradingsymbol':{},'liveTableExists':False, 'infoTableExists':False,
          'listtokens':[],'df_orders':None, 'df_holdings':None,'df_positions':None,
          'trail':{},'follow':{},'timed':{}}
        with open("instruments.yaml","r") as stream:
            instruments = yaml.safe_load(stream)
            for instrument in instruments:
                for key, value in instrument.items():
                    for exch, token in value.items():
                        tradingsymbol = f"{key}-EQ" if exch =='NSE' else key
                        self.MD['listtokens'].append(f"{exch}|{token}|{tradingsymbol}")
        #for after market hours but code duplicacy
        if aftermarket:
            self.login_using_totp_only(TOTP)
            self.log.info(self.MD)
            #create info table
            c = self.connMem.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS info (
                            tradingsymbol TEXT,
                            ucp INTEGER,
                            lcp INTEGER,
                            PRIMARY KEY (tradingsymbol)
                                )''')
            for i in self.MD['listtokens']:
                c.execute('''INSERT OR IGNORE INTO info (tradingsymbol, ucp, lcp) VALUES (?,?,?)''',
                        (i.rsplit('|', 1)[1],0,0))
            self.connMem.commit()
            self.MD['infoTableExists'] = True
            if not self.MD['liveTableExists'] and self.MD['infoTableExists']:
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
                lastBusDay = lastBusDay.replace(day=6,hour=0, minute=0, second=0, microsecond=0)
                
                for tkn in self.MD['listtokens']:
                    exchange = tkn.split('|')[0]
                    token = tkn.split('|')[1]
                    tradingsymbol = tkn.split('|')[2]
                    ret = self.get_time_price_series(exchange=exchange, token=token, starttime=lastBusDay.timestamp(), interval=1)
                    if ret:
                        for row in ret:
                            if row['stat']=='Ok':
                                tm = datetime.datetime.strptime(row['time'],'%d-%m-%Y %H:%M:%S')
                                minute = SharedMethods.m0915(tm.hour,tm.minute)
                                if minute == 375:
                                    self.MD["ltp"][tradingsymbol]=SharedMethods.rp(row['intc'])
                                c.execute('''INSERT OR IGNORE INTO live (tradingsymbol, minute, openp, highp, lowp, closep, volume) VALUES (?,?,?,?,?,?,?) ''',
                                    (tradingsymbol,minute,
                                    SharedMethods.rp(row['into']),
                                    SharedMethods.rp(row['inth']),
                                    SharedMethods.rp(row['intl']),
                                    SharedMethods.rp(row['intc']),
                                    int(row['intv'])))
                self.connMem.commit()

    def login_using_totp_only(self,TOTP):
        with open("cred.yaml","r") as stream:
            cred = yaml.safe_load(stream)
            ret = self.login(cred['user'],cred['pwd'],TOTP,cred['vc'],cred['apikey'],cred['imei'])
            if not ret:
                msg = "Problemia while trying to log in."
            elif ret['stat']=='Ok':
                msg = "Login successful."
                self.start_websocket(
                        subscribe_callback=self.event_handler_feed_update, 
                        order_update_callback=self.event_handler_order_update,
                        socket_open_callback=self.open_callback,
                        socket_close_callback=self.close_callback
                    )
            return msg
        
    def event_handler_feed_update(self,tick_data):
        if not self.feedOpen:
            return
        if self.MD['df_positions'] is None:
            retp = self.get_positions()
            if retp:
                self.MD['df_positions'] = self.store_positions_data(retp)
                self.log.info("Positions stored.")
        if self.MD['df_orders'] is None:    
            reto = self.get_order_book()
            if reto:
                self.MD['df_orders'] = self.store_orders_data(reto)
                self.log.info("Orders stored.")
        c = self.connMem.cursor()
        if tick_data['t']=='dk' and not self.MD['infoTableExists']:
            self.MD['tradingsymbol'][tick_data['tk']]=tick_data['ts']
            c.execute('''CREATE TABLE IF NOT EXISTS info (
                        tradingsymbol TEXT,
                        ucp INTEGER,
                        lcp INTEGER,
                        PRIMARY KEY (tradingsymbol)
                            )''')
            if 'uc' in tick_data:
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
                if ret:
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
                
                self.MD["ltp"][tradingsymbol]=float(tick_data['lp'])
                
                # trail
                # if diff between current price and followed price is getting bigger then make it smaller
                for key,val in self.MD['follow'].items():
                    if val['tradingsymbol']==tradingsymbol:
                        if float(val['trigger_price'])>float(val['price']):
                            sell_order = 1
                        else:
                            sell_order =-1
                        if abs(self.MD["ltp"][tradingsymbol]-float(val['trigger_price']))>3:
                            ret = self.modify_order(exchange=val['exchange'],
                                                    tradingsymbol=tradingsymbol,
                                                    orderno=key,
                                                    newquantity=val['quantity'],
                                                    newprice_type=val['price_type'],
                                                    newprice=val['price']+sell_order*1, 
                                                    newtrigger_price=float(val['trigger_price'])+sell_order*1)
                            self.MD['follow'][key]['trigger_price']=val['trigger_price']+sell_order*1
                            self.MD['follow'][key]['price']=val['price']+sell_order*1
                            if ret['stat']=='Ok':
                                self.log.info(f'''Follow order {key} modification successful.
                                              New trigger_price and price are {self.MD['follow'][key]['trigger_price']} and
                                              {self.MD['follow'][key]['price']}.''')
                            else:
                                self.log.info(f"Follow order {key} modification unsuccessful.")
                
                #timed expiry
                for key,val in self.MD['timed'].items():
                    if val['tradingsymbol']==tradingsymbol:
                        if val['expiry']<datetime.datetime.now():
                            #cancel
                            r = self.cancel_order(key)
                            del self.MD['timed'][key]
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
            if tick_data['norenordno'] in self.MD['trail'] and tick_data['status']=='COMPLETE':
                ret = self.place_order(buy_or_sell=self.MD['trail'][tick_data['norenordno']]['buy_or_sell'],
                                    product_type=self.MD['trail'][tick_data['norenordno']]['product_type'],
                                    exchange=self.MD['trail'][tick_data['norenordno']]['exchange'],
                                    tradingsymbol=self.MD['trail'][tick_data['norenordno']]['tradingsymbol'],
                                    quantity=self.MD['trail'][tick_data['norenordno']]['quantity'],
                                    discloseqty=self.MD['trail'][tick_data['norenordno']]['discloseqty'],
                                    price_type=self.MD['trail'][tick_data['norenordno']]['price_type'],
                                    price=self.MD['trail'][tick_data['norenordno']]['price'],
                                    trigger_price=self.MD['trail'][tick_data['norenordno']]['trigger_price'],
                                    retention=self.MD['trail'][tick_data['norenordno']]['retention'],
                                    remarks=self.MD['trail'][tick_data['norenordno']]['remarks']
                                    )
                if ret:
                    self.log.info(f"trailing order for {tick_data['norenordno']} is successful which is {ret['norenordno']}.")
                    self.MD['follow'][ret['norenordno']]={'exchange':self.MD['trail'][tick_data['norenordno']]['exchange'],
                                                        'tradingsymbol':self.MD['trail'][tick_data['norenordno']]['tradingsymbol'],
                                                        'trigger_price':self.MD['trail'][tick_data['norenordno']]['trigger_price'],
                                                        'price':self.MD['trail'][tick_data['norenordno']]['price'],
                                                        'quantity':self.MD['trail'][tick_data['norenordno']]['quantity'],
                                                        'price_type':self.MD['trail'][tick_data['norenordno']]['price_type'],
                                                        }
            if tick_data['norenordno'] in self.MD['follow'] and tick_data['status']=='COMPLETE':
                del self.MD['follow'][tick_data['norenordno']]
            if tick_data['norenordno'] in self.MD['timed'] and tick_data['status']=='COMPLETE':
                del self.MD['timed'][tick_data['norenordno']]
            
        else:
            self.MD['df_orders'].loc[self.MD['df_orders'].index.max()+1]=[tick_data['norenordno'],
                                                    tick_data['tsym'],
                                                    tick_data['qty'],
                                                    tick_data['prc'],
                                                    tick_data['status'],
                                                    tick_data['trantype'],None]
    
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
        df = {'tradingsymbol':[],'product':[],'quantity':[],'pnl':[],'s_prdt_ali':[],'exch':[]}
        for row in data:
            if row['stat']=='Ok':
                df['tradingsymbol'].append(row['tsym'])
                df['product'].append(row['s_prdt_ali'])
                df['quantity'].append(int(row['netqty']))
                df['pnl'].append(float(row['rpnl'])+float(row['urmtom']))
                df['s_prdt_ali'].append(row['s_prdt_ali'])
                df['exch'].append(row['exch'])
        return pd.DataFrame(df)

    
    def open_callback(self):
        self.feedOpen = True
        self.log.info('Feed is Open')
        self.subscribe([i.rsplit('|', 1)[0] for i in self.MD['listtokens']],feed_type=2)

    def close_callback(self):
        self.feedOpen = False
        self.log.info('Feed is Close')
        self.connMem.close()
    #incomplete
    def display_orders(self):
        self.log.info(self.MD['df_orders'])
        return True
        
    # incomplete
    def stop_all(self):
        openposcount = 0
        
        for row in self.MD['df_positions'][self.MD['df_positions']['quantity']>0].iterrows():
            match (row[1].s_prdt_ali):
                case 'NRML':
                    prd = 'M'
                case 'CNC':
                    prd = 'C'
                case 'MIS':
                    prd = 'I'
            ret = self.place_order(buy_or_sell='S', product_type=prd,
                                exchange=row[1].exch, tradingsymbol=row[1].tradingsymbol, 
                                quantity=row[1].quantity, discloseqty=0,price_type='MKT',
                                retention='DAY', remarks='stop_all')
            self.log.info(f"{ret['stat']}")     
            openposcount +=1
        self.log.info(f"Counter orders for {openposcount} positions submitted.") 

        openordcount = 0 
        for row in self.MD['df_orders'][self.MD['df_orders']['status']=='OPEN'].iterrows():
            self.cancel_order(row[1].orderno)
            openordcount +=1
        self.log.info(f"{openordcount} orders cancelled.") 

    def trail_order(self,orderno:str,tradingsymbol:str, price:float, trigger_price:float,
                    buy_or_sell:str, product_type='I',
                                exchange='NSE', 
                                quantity=1, discloseqty=0, price_type='SL-LMT', 
                                retention='DAY', remarks='place_order'):
        self.MD['trail'][orderno]={'tradingsymbol':tradingsymbol,'price':price,'trigger_price':trigger_price,
                                   'buy_or_sell':buy_or_sell,'product_type':product_type,
                                'exchange':exchange, 
                                'quantity':quantity, 'discloseqty':discloseqty, 'price_type':price_type, 
                                'retention':retention, 'remarks':remarks}
    
    def make_timed(self,orderno:str,expiry:int,tradingsymbol:str):
        self.MD['timed'][orderno]={'expiry':datetime.datetime.now()+datetime.timedelta(0,expiry),
                                   'tradingsymbol':tradingsymbol}

class Instrument():
    name:str
    exch:str
    tradename:str
    def __init__(self,name:str,exch:str='NSE') -> None:
        self.name = name.upper()
        self.exch = exch.upper()
        self.tradename =  name if self.exch !='NSE' else f'{name}-EQ'
    def priceline(minutes:int=1):
        return [ SharedMethods.rp(301.25),SharedMethods.rp(301.85),SharedMethods.rp(301.75) ]
    
    
    