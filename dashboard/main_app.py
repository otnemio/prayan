import gi, sqlite3, os, sys, yaml, grpc, priyu_pb2, priyu_pb2_grpc
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime, timezone
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from sharedmethods import SharedMethods

class Handler():
    def __init__(self):
        global builder, conn
        self.stub = priyu_pb2_grpc.ChirperStub(grpc.insecure_channel('localhost:50051'))
        conn = sqlite3.connect('../collector/bhav_eq_database.db',check_same_thread=False)
        self.fetch_instruments()
    def b(self,id):
        return builder.get_object(id)
    def pr(self,p):
        return float(p)/100
    def fetch_instruments(self):
        list1 = self.b('lstInstruments1')

        with open("../server/instruments.yaml","r") as stream:
            try:
                instruments = yaml.safe_load(stream)
                for instrument in instruments:
                    print(instrument)
                    for key, value in instrument.items():
                        button = Gtk.Button.new_with_label(key)
                        button.connect("pressed",self.display_instrument)
                        for exch, token in value.items():
                            print(exch,token)
                    row = Gtk.ListBoxRow()
                    row.add(button)
                    list1.insert(row,-1)
            except:
                print(exec)
        list1.show_all()
    def display_instrument(self, button):
        heading1 = self.b('lblHeading1')
        symbol = button.get_label()
        heading1.set_text(symbol)
        self.display_historical_chart(symbol)
        self.display_current_chart(symbol)
    
    def display_historical_chart(self, symbol):
        srlMatPlot1 = self.b('scrlHist1')
        c = conn.cursor()
        c.execute('''SELECT * FROM bhav WHERE symbol = ?''',(symbol,))
        rows = c.fetchall()
        df={'open':[],'close':[],'high':[],'low':[],'date':[]}
        for row in rows:
            df['high'].append(self.pr(row[2]))
            df['low'].append(self.pr(row[3]))
            df['open'].append(self.pr(row[1]))
            df['close'].append(self.pr(row[4]))
            df['date'].append(datetime.strptime(f"{row[7]}-{row[6]}-{row[5]}","%Y-%m-%d"))
            
        df_p = pd.DataFrame(df, index=df['date'])
        
        
        # canvas.mpl_connect('button_press_event', self._on_click)
        # canvas.mpl_connect('motion_notify_event', self._on_motion)
        # canvas.mpl_connect('pick_event', self._on_pick)
        # canvas.set_size_request(800, 600)
        # for child in srlMatPlot1.get_children():
        #     srlMatPlot1.remove(child)
        if not srlMatPlot1.get_children():
            fig, ax = plt.subplots()
            canvas = FigureCanvas(fig)  # a Gtk.DrawingArea
            self.axH = ax
            self.canvasH = canvas
            srlMatPlot1.add(canvas)
            srlMatPlot1.show_all()
        self.axH.cla()
        mpf.plot(df_p, ax=self.axH, returnfig=True)
        
        self.canvasH.draw()
        self.canvasH.flush_events()
        
    def display_current_chart(self, symbol):
        srlMatPlot2 = self.b('scrlCurr1')
        req = priyu_pb2.SRequest(symbol=symbol,exchange='NSE')
        res = self.stub.LiveData(req)
        df={'time':[],'open':[],'close':[],'high':[],'low':[],'volume':[]}
        for row in res.ohlcv:
            df['time'].append(datetime.fromtimestamp(row.time.seconds,tz=timezone.utc))
            df['open'].append(SharedMethods.pr(row.pOpen))
            df['high'].append(SharedMethods.pr(row.pHigh))
            df['low'].append(SharedMethods.pr(row.pLow))
            df['close'].append(SharedMethods.pr(row.pClose))
            df['volume'].append(row.volume)
        df_p = pd.DataFrame(df, index=df['time'])
        
        # canvas.mpl_connect('button_press_event', self._on_click)
        # canvas.mpl_connect('motion_notify_event', self._on_motion)
        # canvas.mpl_connect('pick_event', self._on_pick)
        # canvas.set_size_request(800, 600)
        if not srlMatPlot2.get_children():
            fig, ax = plt.subplots()
            canvas = FigureCanvas(fig)  # a Gtk.DrawingArea
            self.axC = ax
            self.canvasC = canvas
            srlMatPlot2.add(canvas)
            srlMatPlot2.show_all()
        self.axC.cla()
        mpf.plot(df_p, ax=self.axC, returnfig=True)
        
        self.canvasC.draw()
        self.canvasC.flush_events()
class App(Gtk.Application):
    __gtype_name__ = 'DashBoard'

    def __init__(self):
        global builder
        
        Gtk.Application.__init__(self,application_id="in.otnemio.dashboard")
        self.connect("activate",self.on_activate)
        self.builder = Gtk.Builder()
        builder = self.builder
        self.builder.add_from_file("app.glade")
        self.builder.connect_signals(Handler())

    def on_activate(self, app):
        self.window = self.builder.get_object("appwindow1")
        self.window.maximize()
        self.window.set_application(app)

        self.window.present()


def initialize():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    initialize()
    app = App()
    app.run(sys.argv)