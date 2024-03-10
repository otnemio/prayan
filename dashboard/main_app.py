import gi, sqlite3, os, sys

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

class Handler():
    def __init__(self):
        global builder

    def onButtonPressed(self, button):
        print("Hello World!")


class App(Gtk.Application):
    __gtype_name__ = 'DashBoard'

    def __init__(self):
        global builder
        
        Gtk.Application.__init__(self,application_id="in.otnemio.dashboard")
        self.connect("activate",self.on_activate)
        self.builder = Gtk.Builder()
        self.builder.add_from_file("app.glade")
        self.builder.connect_signals(Handler())

        builder = self.builder

            
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