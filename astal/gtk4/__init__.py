# https://github.com/wmww/gtk4-layer-shell/issues/3
# gtk4-layer-shell.so must be linked prior to libwayland-client.so
from ctypes import CDLL
CDLL('libgtk4-layer-shell.so')

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Astal", "4.0")

from astal.gtk4.app import App
from astal.gtk4.astalify import astalify
import astal.gtk4.widget as Widget

from gi.repository import Gtk, Gdk, Astal

