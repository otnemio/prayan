import gi, sqlite3, os, sys, yaml
import pandas as pd
import mplfinance as mpf
from datetime import datetime
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

class Handler():
    def __init__(self):
        global builder, conn
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
        
        fig, ax = mpf.plot(df_p, figratio=(8, 5), returnfig=True)
        
        
        canvas = FigureCanvas(fig)  # a Gtk.DrawingArea
        # canvas.mpl_connect('button_press_event', self._on_click)
        # canvas.mpl_connect('motion_notify_event', self._on_motion)
        # canvas.mpl_connect('pick_event', self._on_pick)
        # canvas.set_size_request(800, 600)
        for child in srlMatPlot1.get_children():
            srlMatPlot1.remove(child)
        if not srlMatPlot1.get_children():
            srlMatPlot1.add(canvas)
        # canvas.draw()
        self.figure = fig
        self.ax = ax
        srlMatPlot1.show_all()
    
    def display_current_chart(self, symbol):
        pass


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