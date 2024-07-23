from shoonya import ShoonyaApi, Instrument
from logger import logger
from flask import Flask,jsonify,request 
from waitress import serve
import os, yaml, sys, threading, datetime, time

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
            with open("cred.yaml","r") as stream:
                cred = yaml.safe_load(stream)
                ret = api.login(cred['user'],cred['pwd'],request.args.get('totp'),cred['vc'],cred['apikey'],cred['imei'])
                if not ret:
                    status = 'NOK'
                    msg = "Problemia while trying to log in."
                elif ret['stat']=='Ok':
                    msg = "Login successful."
                    api.start_websocket(
                            subscribe_callback=api.event_handler_feed_update, 
                            order_update_callback=api.event_handler_order_update,
                            socket_open_callback=api.open_callback,
                            socket_close_callback=api.close_callback
                        )
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

@app.route('/s/<name>', methods = ['GET']) 
def Live(name): 
    if(request.method == 'GET'):
        if hasattr(api,'_NorenApi__username'):
            status = 'OK'
            s = name.upper()
            ins = Instrument(s)
            msg = { "Instrument":s,
                    "LTP":api.MD["ltp"][ins.tradename] if ins.tradename in api.MD["ltp"] else None}
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
    # app.run(debug=True)
    initialize()
    t = threading.Thread(target=trade,args=())
    t.start()
    serve(app=app,host="0.0.0.0", port=sys.argv[1] if len(sys.argv)>1 else 8081)
    t.join()