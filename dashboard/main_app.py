import matplotlib, gi, sqlite3, os, sys, yaml, grpc, priyu_pb2, priyu_pb2_grpc
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime, timezone, time
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.patches import Rectangle, Ellipse, Circle
from gi.repository import Gtk, Gdk, GLib
gi.require_version("Gtk", "3.0")
from sharedmethods import SharedMethods

class Handler():
    def __init__(self):
        global builder, conn, MD
        MD = {'childorders':[],'positions':[],'holdings':[]}
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
            instruments = yaml.safe_load(stream)
            for instrument in instruments:
                for key, value in instrument.items():
                    button = Gtk.Button.new_with_label(key)
                    button.connect("pressed",self.display_instrument)
                row = Gtk.ListBoxRow()
                row.add(button)
                list1.insert(row,-1)
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
            fig.tight_layout()
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
        # canvas.set_size_request(800, 600)
        if not srlMatPlot2.get_children():
            fig, ax = plt.subplots()
            canvas = FigureCanvas(fig)  # a Gtk.DrawingArea
            self.axC = ax
            self.canvasC = canvas
            self.figC = fig
            # fix twice init issue
            self.tool = {'circles':[],'rectangles':[],'selected_circle':None}
            canvas.mpl_connect('button_press_event', self.on_click)
            canvas.mpl_connect('motion_notify_event', self.on_motion)
            canvas.mpl_connect('button_release_event', self.on_release)
            srlMatPlot2.add(canvas)
            srlMatPlot2.show_all()
        
        self.update_chart()
    
    def on_motion(self, event):
        if self.tool['selected_circle'] is not None:
            c1 = self.tool['circles'][0]
            c2 = self.tool['circles'][1]
            c3 = self.tool['circles'][2]
            c4 = self.tool['circles'][3]
            match self.tool['selected_circle'].get_label():
                case 'c1':
                    c1.center = (event.xdata, event.ydata)
                    c4.center = (event.xdata+self.tool['rectangles'][0].get_width(), event.ydata)
                    c2.center = (event.xdata, c2.center[1])
                    c3.center = (event.xdata, c3.center[1])
                    self.tool['rectangles'][0].set_xy((event.xdata, event.ydata))
                    self.tool['rectangles'][0].set_height(c2.center[1]-c1.center[1])
                    self.tool['rectangles'][1].set_xy((event.xdata, event.ydata))
                    self.tool['rectangles'][1].set_height(c3.center[1]-c1.center[1])
                case 'c2':
                    self.tool['selected_circle'].center = (self.tool['selected_circle'].center[0], event.ydata)
                    self.tool['rectangles'][0].set_height(c2.center[1]-c1.center[1])
                case 'c3':
                    self.tool['selected_circle'].center = (self.tool['selected_circle'].center[0], event.ydata)    
                    self.tool['rectangles'][1].set_height(c3.center[1]-c1.center[1])
                case 'c4':
                    self.tool['selected_circle'].center = (event.xdata, self.tool['selected_circle'].center[1])
                    self.tool['rectangles'][0].set_width(c4.center[0]-c1.center[0])
                    self.tool['rectangles'][1].set_width(c4.center[0]-c1.center[0])
                
            self.canvasC.draw_idle()
    def on_release(self, event):
        if self.tool['selected_circle'] is not None:
            self.tool['selected_circle'] = None
    def on_click(self, event):
        btnSL1 = self.b('btnSL1')
        lblSL1 = self.b('lblSL1')
        if event.button == 1:
            if btnSL1.get_active():
                lblSL1.set_text(str(int(event.ydata*20)/20.0))
                btnSL1.set_active(False)
            x = event.xdata
            y = event.ydata
            for circle in self.tool['circles']:
                if circle.contains(event)[0]:
                    circle.set_color('red')
                    self.tool['selected_circle'] = circle
                else:
                    circle.set_color('pink')
            self.canvasC.draw_idle()
            
        
    def update_chart(self):
        if not self.connected:
            return
        srlMatPlot2 = self.b('scrlCurr1')
        lblHeading1 = self.b('lblHeading1')
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
            for row in MD['childorders']:
                print(row)
                if row.tradingsymbol.split('-')[0] == lblHeading1.get_text() and row.status=='COMPLETE':
                    tm = datetime.fromtimestamp(row.childordertime.seconds)
                    self.create_orders_markers(x=SharedMethods.m0915(tm.hour,tm.minute),y=row.p5Price/20.0,
                                               text=row.quantity, type=row.type )
            self.canvasC.draw_idle()

    def create_ranged_bracket(self,x,y):
        
        updis = 1
        downdis= 0.5
        fardis = 30
        origin = (x,y)
        over = (x,y+updis)
        below = (x,y-downdis)
        far = (x+fardis,y)
        
        
        xscale, yscale = self.axC.transData.transform([1, 1]) - self.axC.transData.transform([0, 0])
        radius_x = 4
        radius_y = radius_x * xscale / yscale
        
        c1 = Ellipse(origin, radius_x, radius_y,color='pink',alpha=0.8,label='c1')
        c2 = Ellipse(over, radius_x, radius_y,color='pink',alpha=0.8,label='c2')
        c3 = Ellipse(below, radius_x, radius_y,color='pink',alpha=0.8,label='c3')
        c4 = Ellipse(far, radius_x, radius_y,color='pink',alpha=0.8,label='c4')
        
        rect1 = Rectangle(origin,fardis,updis, color='green',alpha=0.3)
        rect2 = Rectangle(origin,fardis,-downdis, color ='blue', alpha=0.3)
        self.tool['circles'].append(c1)
        self.tool['circles'].append(c2)
        self.tool['circles'].append(c3)
        self.tool['circles'].append(c4)
        self.tool['rectangles'].append(rect1)
        self.tool['rectangles'].append(rect2)
        
        self.axC.add_patch(c1)
        self.axC.add_patch(c2)
        self.axC.add_patch(c3)
        self.axC.add_patch(c4)
        self.axC.add_patch(rect1)
        self.axC.add_patch(rect2)
        
        self.canvasC.draw_idle()
    
    def create_orders_markers(self,x,y,text,type):
        # plt.text(x, y, text, color='red' if type else 'green',fontsize=8)
        self.axC.annotate(text,  xy=(x, y), color='red' if type else 'green',
                fontsize="small", weight='light',
                horizontalalignment='center',
                verticalalignment='center')
        
    def create_orders(self, button):
        self.tool = {'circles':[],'rectangles':[],'selected_circle':None}
        #fill x and y value from somewhere
        self.create_ranged_bracket(90,240)
    
    def higher(self, button):
        lblHeading1 = self.b('lblHeading1')
        entrySL1 = self.b('entrySL1')
        spinPercent1 = self.b('spinPercent1')
        active_radios = [r for r in self.b('radiobuttonUp1').get_group() if r.get_active()]
        req = priyu_pb2.OrderRequest(symbol=lblHeading1.get_text(),
                                     type=priyu_pb2.Type.BUY,
                                     p5Trigger=0,
                                     p5Target=0,
                                     p5StopLoss=int(float(entrySL1.get_text())*20),
                                     steps=active_radios[0].get_name(),
                                     qtyPercent=int(spinPercent1.get_text()))
        res = self.stub.BracketOrder(req)
        if res:
            print("Order submission successful.")

    def lower(self, button):
        lblHeading1 = self.b('lblHeading1')
        entrySL1 = self.b('entrySL1')
        spinPercent1 = self.b('spinPercent1')
        active_radios = [r for r in self.b('radiobuttonDown1').get_group() if r.get_active()]
        req = priyu_pb2.OrderRequest(symbol=lblHeading1.get_text(),
                                     type=priyu_pb2.Type.SELL,
                                     p5Trigger=0,
                                     p5Target=0,
                                     p5StopLoss=int(float(entrySL1.get_text())*20),
                                     steps=active_radios[0].get_name(),
                                     qtyPercent=int(spinPercent1.get_text()))
        res = self.stub.BracketOrder(req)
        if res:
            print("Order submission successful.")

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
        column = Gtk.TreeViewColumn("Orders")

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
        boxOrders1.add(tree)
        
        req = priyu_pb2.PRequest(msg='')
        res = self.stub.ChildOrdersStatus(req)
        MD['childorders'] = []
        store = Gtk.ListStore(str, int, str, str, str, str)
        for row in res.childorder:
            MD['childorders'].append(row)
            tm = datetime.fromtimestamp(row.childordertime.seconds)
            store.append([row.tradingsymbol, row.quantity,
                          f"{row.p5Price/20.0:.2f}", row.status, f"{priyu_pb2.Type.Name(row.type)}",
                          f"{tm.hour}:{tm.minute}:{tm.second}"])
        tree = Gtk.TreeView(model=store)
        column = Gtk.TreeViewColumn("Child Orders")
        orderno = Gtk.CellRendererText()
        tradingsymbol = Gtk.CellRendererText()
        quantity = Gtk.CellRendererText()
        price = Gtk.CellRendererText()
        price.set_property('xalign',1)
        status = Gtk.CellRendererText()
        type = Gtk.CellRendererText()
        childordertime = Gtk.CellRendererText()
        
        column.pack_start(tradingsymbol, True)
        column.pack_start(quantity, True)
        column.pack_start(price, True)
        column.pack_start(status, True)
        column.pack_start(type, True)
        column.pack_start(childordertime, True)
        
        column.add_attribute(tradingsymbol, "text", 0)
        column.add_attribute(quantity, "text", 1)
        column.add_attribute(price, "text", 2)
        column.add_attribute(status, "text", 3)
        column.add_attribute(type, "text", 4)
        column.add_attribute(childordertime, "text", 5)
        
        tree.append_column(column)
        boxOrders1.add(tree)
        select = tree.get_selection()
        select.connect("changed", self.on_tree_selection_changed)
        boxOrders1.show_all()

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected", model[treeiter][0])
    
    def update_posholds(self):
        boxPosHold1 = self.b('boxPosHold1')
        req = priyu_pb2.PRequest(msg='positions')
        res = self.stub.PosHold(req)
        for child in boxPosHold1.get_children():
            boxPosHold1.remove(child)
        
        store = Gtk.ListStore(str, str, int, str)
        
        for quant in res.quant:
            store.append([quant.tradingsymbol, quant.product, quant.quantity, f"{quant.pnl:.2f}"])
        tree = Gtk.TreeView(model=store)
        column = Gtk.TreeViewColumn("Positions")

        tradingsymbol = Gtk.CellRendererText()
        product = Gtk.CellRendererText()
        quantity = Gtk.CellRendererText()
        pnl = Gtk.CellRendererText()
        pnl.set_property('xalign',1)
        
        column.pack_start(tradingsymbol, True)
        column.pack_start(product, True)
        column.pack_start(quantity, True)
        column.pack_start(pnl, True)
        column.add_attribute(tradingsymbol, "text", 0)
        column.add_attribute(product, "text", 1)
        column.add_attribute(quantity, "text", 2)
        column.add_attribute(pnl, "text", 3)
        tree.append_column(column)
        
        boxPosHold1.add(tree)
        
        req = priyu_pb2.PRequest(msg='holdings')
        res = self.stub.PosHold(req)
        store = Gtk.ListStore(str, str, int)
        for quant in res.quant:
            store.append([quant.tradingsymbol, quant.product, quant.quantity])
        # store.append(["BEL","CNC",100])
        # store.append(["BHEL","CNC",200])
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
        print("Application closed successfully.")

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