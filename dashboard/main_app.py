import matplotlib, gi, sqlite3, os, sys, yaml, grpc, priyu_pb2, priyu_pb2_grpc
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
        # Set the backend to GTK
        matplotlib.use('GTK3Agg')
        self.fetch_instruments()
        self.connected = False
        self.try_connecting()
        self.refresh(None)
    
    def try_connecting(self):
        req = priyu_pb2.PRequest(msg='Connect')
        try:
            res = self.stub.Command(req)
            if res:
                self.b('lblConnectionStatus1').set_label('Connected')
                self.connected = True
            else:
                self.b('lblConnectionStatus1').set_label('Problem Connecting')
        except:
            self.b('lblConnectionStatus1').set_label('Not Connected')
    
    def connect(self,button):
        self.try_connecting()
        
    def b(self,id):
        return builder.get_object(id)
    
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
            df['high'].append(SharedMethods.pr(row[2]))
            df['low'].append(SharedMethods.pr(row[3]))
            df['open'].append(SharedMethods.pr(row[1]))
            df['close'].append(SharedMethods.pr(row[4]))
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
        mpf.plot(df_p, ax=self.axH, returnfig=True, xrotation=0)
        self.canvasH.draw()
        self.canvasH.flush_events()
        
    def display_current_chart(self, symbol):
        srlMatPlot2 = self.b('scrlCurr1')
        self.symbol = symbol
        self.chart_style = self.get_style()
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
        self.update_chart()
    
    def update_chart(self):
        if not self.connected:
            return
        srlMatPlot2 = self.b('scrlCurr1')
        if srlMatPlot2.get_children():
            req = priyu_pb2.SRequest(symbol=self.symbol,exchange='NSE')
            res = self.stub.LiveData(req)
            df={'time':[], 'open':[], 'high':[], 'low':[], 'close':[], 'volume':[]}
            if not res.ohlcv:
                return
            for row in res.ohlcv:
                df['time'].append(datetime.fromtimestamp(row.time.seconds,tz=timezone.utc))
                df['open'].append(SharedMethods.pr(row.pOpen))
                df['high'].append(SharedMethods.pr(row.pHigh))
                df['low'].append(SharedMethods.pr(row.pLow))
                df['close'].append(SharedMethods.pr(row.pClose))
                df['volume'].append(row.volume)
            df_p = pd.DataFrame(df, index=df['time'])
            self.axC.cla()
            mpf.plot(df_p, ax=self.axC, returnfig=True, xrotation=0, style=self.chart_style)
            self.canvasC.draw()
            self.canvasC.flush_events()
    
    def update_orders(self):
        boxOrders1 = self.b('boxOrders1')
        req = priyu_pb2.PRequest(msg='')
        # res = self.stub.AllOrdersStatus(req)
        for child in boxOrders1.get_children():
            boxOrders1.remove(child)
        store = Gtk.TreeStore(str, str, int)
        st1 = store.append(None,["BEL","",50])
        store.append(st1,["BEL","MIS",10])
        store.append(st1,["BEL","MIS",40])
        store.append(None,["BHEL","CNC",20])
        tree = Gtk.TreeView(model=store)
        column1 = Gtk.TreeViewColumn("Orders")

        tradingsymbol = Gtk.CellRendererText()
        product = Gtk.CellRendererText()
        quantity = Gtk.CellRendererText()
        column1.pack_start(tradingsymbol, True)
        column1.pack_start(product, True)
        column1.pack_start(quantity, True)
        column1.add_attribute(tradingsymbol, "text", 0)
        column1.add_attribute(product, "text", 1)
        column1.add_attribute(quantity, "text", 2)
        
        tree.append_column(column1)
        
        boxOrders1.add(tree)
        boxOrders1.show_all()

    def update_posholds(self):
        boxPosHold1 = self.b('boxPosHold1')
        req = priyu_pb2.PRequest(msg='positions')
        # res = self.stub.PosHold(req)
        for child in boxPosHold1.get_children():
            boxPosHold1.remove(child)
        
        store = Gtk.ListStore(str, str, int)
        # for quant in res.quant:
        #     store.append([quant.tradingsymbol, quant.product, quant.quantity])
        store.append(["BEL","MIS",10])
        store.append(["BHEL","CNC",20])
        tree = Gtk.TreeView(model=store)
        column = Gtk.TreeViewColumn("Positions")

        tradingsymbol = Gtk.CellRendererText()
        product = Gtk.CellRendererText()
        quantity = Gtk.CellRendererText()
        column.pack_start(tradingsymbol, True)
        column.pack_start(product, True)
        column.pack_start(quantity, True)
        column.add_attribute(tradingsymbol, "text", 0)
        column.add_attribute(product, "text", 1)
        column.add_attribute(quantity, "text", 2)
        tree.append_column(column)
        
        boxPosHold1.add(tree)
        
        store = Gtk.ListStore(str, str, int)
        # for quant in res.quant:
        #     store.append([quant.tradingsymbol, quant.product, quant.quantity])
        store.append(["BEL","CNC",100])
        store.append(["BHEL","CNC",200])
        tree = Gtk.TreeView(model=store)
        column = Gtk.TreeViewColumn("Holdings")

        tradingsymbol = Gtk.CellRendererText()
        product = Gtk.CellRendererText()
        quantity = Gtk.CellRendererText()
        column.pack_start(tradingsymbol, True)
        column.pack_start(product, True)
        column.pack_start(quantity, True)
        column.add_attribute(tradingsymbol, "text", 0)
        column.add_attribute(product, "text", 1)
        column.add_attribute(quantity, "text", 2)
        tree.append_column(column)
        
        boxPosHold1.add(tree)
        boxPosHold1.show_all()

    def refresh(self, button):
        self.update_chart()
        self.update_posholds()
        self.update_orders()

    def get_style(self):
        active_radios = [r for r in self.b('radiomenuitem1').get_group() if r.get_active()]
        return active_radios[0].get_label()
    
    def close_application(self, event, data):
        plt.close('all')
        print("Exit complete")
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
        self.apply_css()
        self.window.present()
    
    def apply_css(self):
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        try:
            css_provider.load_from_path('main.css')
            context = Gtk.StyleContext()
            context.add_provider_for_screen(screen, css_provider,
                                            Gtk.STYLE_PROVIDER_PRIORITY_USER)
        except GLib.Error as e:
            print(f"Error in theme: {e} ")
    


def initialize():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    initialize()
    app = App()
    app.run(sys.argv)