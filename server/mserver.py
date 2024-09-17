from shoonya import ShoonyaApi, Instrument
from logger import logger
from flask import Flask,jsonify,request 
from waitress import serve
import os, yaml, sys, threading, datetime, time, random, csv
from rich.prompt import Prompt

app =   Flask(__name__) 
  
@app.route('/', methods = ['GET']) 
def Main(): 
    if(request.method == 'GET'):
        data = { 
            'Status' : 'OK',
            'Msg' : 'Server running.', 
        }
        return jsonify(data)

@app.route('/loggedin', methods = ['GET']) 
def Status(): 
    if(request.method == 'GET'):
        if hasattr(api,'_NorenApi__username'):
            status = 'OK'
            msg = "Logged in."
        else:
            status = 'NOK'
            msg = "Not logged in."
        data = { 
            'Status' : status,
            'Msg' : msg, 
        }
        return jsonify(data)

@app.route('/login', methods = ['GET']) 
def Login(): 
    if(request.method == 'GET'):
        status = 'OK'
        if hasattr(api,'_NorenApi__username'):
            msg = "Already loggedin."
        else:
            msg = api.login_using_totp_only(request.args.get('totp'))
        data = { 
            'Status' : status,
            'Msg' : msg, 
        }
        return jsonify(data)

@app.route('/holdings', methods = ['GET']) 
def Holdings(): 
    if(request.method == 'GET'):
        if hasattr(api,'_NorenApi__username'):
            status = 'OK'
            ret = api.get_holdings()
            if not ret:
                    status = 'NOK'
                    msg = "Problemia while trying to fetch holdings."
            elif ret[0]['stat']=='Ok':
                    msg = ret
        else:
            status = 'NOK'
            msg = "Not logged in."
        data = { 
            'Status' : status,
            'Msg' : msg, 
        }
        return jsonify(data)

@app.route('/limits', methods = ['GET']) 
def Limits(): 
    if(request.method == 'GET'):
        if hasattr(api,'_NorenApi__username'):
            status = 'OK'
            ret = api.get_limits()
            if not ret:
                    status = 'NOK'
                    msg = "Problemia while trying to fetch limits."
            elif ret['stat']=='Ok':
                    msg = ret
        else:
            status = 'NOK'
            msg = "Not logged in."
        data = { 
            'Status' : status,
            'Msg' : msg, 
        }
        return jsonify(data)

@app.route('/btst', methods = ['GET']) 
def Btst(): 
    if(request.method == 'GET'):
        if hasattr(api,'_NorenApi__username'):
            status = 'OK'
            s = request.args.get('s').upper()
            msg = f'Buy levels submitted for {s} which are {request.args.get("l")}.'
        else:
            status = 'NOK'
            msg = "Not logged in."
        data = { 
            'Status' : status,
            'Msg' : msg,
        }
        return jsonify(data)

@app.route('/stop_all', methods = ['GET']) 
def StopAll():
    if(request.method == 'GET'):
        if hasattr(api,'_NorenApi__username'):
            status = 'OK'
            msg = "Cacelled all pending orders successfully."
            api.stop_all()
        else:
            status = 'NOK'
            msg = "Not logged in."
        data = { 
            'Status' : status,
            'Msg' : msg,
        }
        return jsonify(data)

@app.route('/aftermarket', methods = ['GET']) 
def AfterMarket():
    if(request.method == 'GET'):
        if hasattr(api,'_NorenApi__username'):
            status = 'OK'
            msg = api.aftermarket()
        else:
            status = 'NOK'
            msg = "Not logged in."
        data = { 
            'Status' : status,
            'Msg' : msg,
        }
        return jsonify(data)


@app.route('/fnolist', methods = ['GET']) 
def FnOList():
    if(request.method == 'GET'):
        # Open the CSV file
        with open('data/fnolots.csv', 'r') as csv_file:
            # Create a CSV reader
            csv_reader = csv.DictReader(csv_file)

            # Create a list of dictionaries to store the JSON data
            json_data = []

            # Iterate over the CSV rows
            for row in csv_reader:
                # Append each row (as a dictionary) to the list
                json_data.append(row)
        return json_data

@app.route('/orders', methods = ['GET']) 
def Orders():
    if(request.method == 'GET'):
        if hasattr(api,'_NorenApi__username'):
            status = 'OK'
            r = api.display_orders()
            msg = f"Orders display {'un' if not r else ''}successful."
        else:
            status = 'NOK'
            msg = "Not logged in."
        data = { 
            'Status' : status,
            'Msg' : msg,
        }
        return jsonify(data)

@app.route('/s/<name>', methods = ['GET']) 
def Live(name): 
    if(request.method == 'GET'):
        if hasattr(api,'_NorenApi__username'):
            status = 'OK'
            s = name.upper().rsplit('-')[0]
            ins = Instrument(s)
            msg = { "Instrument":s,
                    "LTP":api.MD["ltp"][ins.tradename] if ins.tradename in api.MD["ltp"] else None,
                    "PriceLine":ins.priceline(),
                    "OHLCV":{0:(2,5,2,5,500),1:(5,6,2,3,300)}}
        else:
            status = 'NOK'
            msg = "Not logged in."
        data = { 
            'Status' : status,
            'Msg' : msg,
        }
        return jsonify(data)

# /to/BANKEX2490961200PE?bos=b&t=o&q=20&fq=10&p=304.15&tp=304.05&slp=303.75&sltp=303.85&fp=305
@app.route('/to/<tradingsymbol>', methods = ['GET']) 
def TrailOrder(tradingsymbol:str): 
    if(request.method == 'GET'):
        if hasattr(api,'_NorenApi__username'):
            status = 'OK'
            match request.args.get('t'):
                case 'o':
                    ret = api.place_order(buy_or_sell='B' if request.args.get('bos')=='b' else 'S',
                                            product_type='M',
                            exchange='BFO' if tradingsymbol.startswith('SENSEX') else 'NFO', tradingsymbol=tradingsymbol, 
                            quantity=int(request.args.get('q')), discloseqty=0, price_type='SL-LMT', 
                            price=float(request.args.get('p')), trigger_price=float(request.args.get('tp')),
                            retention='DAY', remarks='place_order')
                    if ret:
                        api.log.info(f"Trail order placed successfully {ret['norenordno']}")
                        api.trail_order(ret['norenordno'],buy_or_sell='S' if request.args.get('bos')=='b' else 'B',
                                        product_type='M',
                            exchange='BFO' if tradingsymbol.startswith('SENSEX') else 'NFO', tradingsymbol=tradingsymbol, 
                            quantity=int(request.args.get('q')), discloseqty=0, price_type='SL-LMT', 
                            price=float(request.args.get('slp')), trigger_price=float(request.args.get('sltp')),
                            retention='DAY', remarks='place_order')
                        api.forward_order(ret['norenordno'],buy_or_sell='S' if request.args.get('bos')=='b' else 'B',
                                        product_type='M',
                            exchange='BFO' if tradingsymbol.startswith('SENSEX') else 'NFO', tradingsymbol=tradingsymbol, 
                            quantity=int(request.args.get('fq')), discloseqty=0, price_type='LMT', 
                            price=float(request.args.get('fp')),
                            retention='DAY', remarks='place_order')
                case 'mo':
                    ret = api.place_order(buy_or_sell='B' if request.args.get('bos')=='b' else 'S',
                                            product_type='M',
                            exchange='MCX', tradingsymbol=tradingsymbol, 
                            quantity=int(request.args.get('q')), discloseqty=0, price_type='SL-LMT', 
                            price=float(request.args.get('p')), trigger_price=float(request.args.get('tp')),
                            retention='DAY', remarks='place_order')
                    if ret:
                        api.log.info(f"Trail order placed successfully {ret['norenordno']}")
                        api.trail_order(ret['norenordno'],buy_or_sell='S' if request.args.get('bos')=='b' else 'B',
                                        product_type='M',
                            exchange='MCX', tradingsymbol=tradingsymbol, 
                            quantity=int(request.args.get('q')), discloseqty=0, price_type='SL-LMT', 
                            price=float(request.args.get('slp')), trigger_price=float(request.args.get('sltp')),
                            retention='DAY', remarks='place_order')
                        api.forward_order(ret['norenordno'],buy_or_sell='S' if request.args.get('bos')=='b' else 'B',
                                        product_type='M',
                            exchange='MCX', tradingsymbol=tradingsymbol, 
                            quantity=int(request.args.get('fq')), discloseqty=0, price_type='LMT', 
                            price=float(request.args.get('fp')),
                            retention='DAY', remarks='place_order')
                case 'e':
                    ret = api.place_order(buy_or_sell='B' if request.args.get('bos')=='b' else 'S',
                                            product_type='I',
                            exchange='NSE', tradingsymbol=tradingsymbol, 
                            quantity=int(request.args.get('q')), discloseqty=0, price_type='SL-LMT', 
                            price=float(request.args.get('p')), trigger_price=float(request.args.get('tp')),
                            retention='DAY', remarks='place_order')
                    if ret:
                        api.log.info(f"Trail order placed successfully {ret['norenordno']}")
                        api.trail_order(ret['norenordno'],buy_or_sell='S' if request.args.get('bos')=='b' else 'B',
                                        product_type='I',
                            exchange='NSE', tradingsymbol=tradingsymbol, 
                            quantity=int(request.args.get('q')), discloseqty=0, price_type='SL-LMT', 
                            price=float(request.args.get('slp')), trigger_price=float(request.args.get('sltp')),
                            retention='DAY', remarks='place_order')
                        api.forward_order(ret['norenordno'],buy_or_sell='S' if request.args.get('bos')=='b' else 'B',
                                        product_type='I',
                            exchange='NSE', tradingsymbol=tradingsymbol, 
                            quantity=int(request.args.get('fq')), discloseqty=0, price_type='LMT', 
                            price=float(request.args.get('fp')),
                            retention='DAY', remarks='place_order')
            
            msg = "Order punched."
        else:
            status = 'NOK'
            msg = "Not logged in."
        data = { 
            'Status' : status,
            'Msg' : msg,
        }
        return jsonify(data)


def initialize():  
    global log, api 
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    log = logger()
    api = ShoonyaApi()

def trade():
    log.info("Trading")
    while True:
        now = datetime.datetime.now()
        time.sleep(1)
        # print(s.spot)
        

if __name__=='__main__':
    initialize()
    t = threading.Thread(target=trade,args=())
    t.start()
    serve(app=app,host="0.0.0.0", port=sys.argv[1] if len(sys.argv)>1 else 8081)
    t.join()