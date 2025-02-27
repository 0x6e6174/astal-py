from astal.gtk4.astalify import astalify
from enum import Enum

from gi.repository import Astal, Gtk

class CallableEnum(Enum):
    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)

class Widget(CallableEnum):
    Box = astalify(Astal.Box)
    Button = astalify(Gtk.Button)
    CenterBox = astalify(Gtk.CenterBox)
    # CircularProgress = astalify(Gtk.CircularProgress)
    DrawingArea = astalify(Gtk.DrawingArea)
    Entry = astalify(Gtk.Entry)
    # EventBox = astalify(Gtk.EventBox)
    # Icon = astalify(Gtk.Icon)
    Label = astalify(Gtk.Label)
    LevelBar = astalify(Gtk.LevelBar)
    MenuButton = astalify(Gtk.MenuButton)
    Overlay = astalify(Gtk.Overlay)
    Revealer = astalify(Gtk.Revealer)
    # Scrollable = astalify(Gtk.Scrollable)
    Slider = astalify(Astal.Slider)
    Stack = astalify(Gtk.Stack)
    Switch = astalify(Gtk.Switch)
    Window = astalify(Gtk.Window)
