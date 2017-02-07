import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from controller.UIHandler import UIHandler
from os.path import abspath, dirname, join

# from data.Strings import Strings
import locale
import gettext

# Paths
appName = 'main'
basePath = abspath(dirname(__file__))
localePath = join(basePath, 'po')
gladeFile = join(basePath,'glade/main.glade')

locale.setlocale(locale.LC_ALL,'')
gettext.bindtextdomain(appName,localePath)
locale.bindtextdomain(appName,localePath)
gettext.textdomain(appName)
_ = gettext.gettext
N_ = gettext.ngettext

## Cargo UI
builder = Gtk.Builder()
builder.set_translation_domain(appName)
builder.add_from_file(gladeFile)
builder.connect_signals(UIHandler(builder))

## Main
window = builder.get_object("window_main")
window.set_default_size(500, 400)
window.show_all()
Gtk.main()
