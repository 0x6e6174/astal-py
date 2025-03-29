from astal.gtk4.astalify import astalify
from enum import Enum

from gi.repository import Astal, Gtk

def filter_children(children):
    return map(lambda x: x if isinstance(x, Gtk.Widget) else Gtk.Label(visible=True, label=x), children)

def _centerbox_get_children(self):
    return self.start_widget, self.center_widget, self.end_widget

def _centerbox_set_children(self, children):
    children = filter_children(children)
    self.start_widget = children[0] or Gtk.Box()
    self.center_widget = children[1] or Gtk.Box()
    self.end_widget = children[2] or Gtk.Box()

Box = astalify(Astal.Box)
Button = astalify(Gtk.Button)
CenterBox = astalify(Gtk.CenterBox, dict(
    get_children = _centerbox_get_children,
    set_children = _centerbox_set_children
))
# CircularProgress = astalify(Gtk.CircularProgress)
# DrawingArea = astalify(Gtk.DrawingArea)
Entry = astalify(Gtk.Entry, dict(get_children = lambda _: []))
# EventBox = astalify(Gtk.EventBox)
# Icon = astalify(Gtk.Icon)
Image = astalify(Gtk.Image, dict(get_children = lambda _: []))
Label = astalify(Gtk.Label, dict(
    get_children = lambda _: [],
    set_children = lambda self, children: self.set_label(str(children))
))
LevelBar = astalify(Gtk.LevelBar, dict(get_children = lambda _: []))

def _stack_set_children(self, children):
    for child in filter_children(children):
        if isinstance(child, Gtk.Popover):
            self.set_popover(child)

        else:
            self.set_child(child)

MenuButton = astalify(Gtk.MenuButton, dict(
    get_children = lambda self: (self.popover, self.child),
    set_children = _stack_set_children
))

def _overlay_get_children(self):
    children = []
    ch = self.get_first_child()
    while ch != None:
        children.append(ch)
        ch = ch.get_next_sibling

    return filter(lambda child: child != self.child, children)

def _overlay_set_children(self, children):
    for child in filter_children(children):
        types = child.type.split(' ')

        if 'overlay' in types:
            self.add_overlay(child)
        else:
            self.set_child(child)

        self.set_measure_overlay(child, 'measure' in types)
        self.set_clip_overlay(child, 'clip' in types)

Overlay = astalify(Gtk.Overlay, dict(
    get_children = _overlay_get_children,
    set_children = _overlay_set_children
))
Revealer = astalify(Gtk.Revealer, dict(get_children = lambda _: []))
# Scrollable = astalify(Gtk.Scrollable)
Slider = astalify(Astal.Slider, dict(get_children = lambda _: []))

def _stack_set_children(self, children):
    for child in filter_children(children):
        if getattr(child, 'name', None):
            self.add_named(child, child.name)

        else:
            self.add_child(child)

Stack = astalify(Gtk.Stack, dict(set_children = _stack_set_children))
Switch = astalify(Gtk.Switch, dict(get_children = lambda _: []))
Popover = astalify(Gtk.Popover)
Window = astalify(Astal.Window)
