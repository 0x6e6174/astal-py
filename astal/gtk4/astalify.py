from functools import partial

from typing import Callable, TypedDict

from astal.binding import Binding
from astal.variable import Variable

from gi.repository import Astal, Gtk, Gdk, GObject

import ctypes

lib = ctypes.CDLL('/'.join(__file__.split('/')[:-1]) + "/add_child.so")
lib.add_child.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
lib.add_child.restype = ctypes.c_void_p
add_child = lambda self, builder, child: lib.add_child(ctypes.c_void_p(hash(self)), ctypes.c_void_p(hash(builder)), ctypes.c_void_p(hash(child)))

_builder = Gtk.Builder()

def _get_children(self):
    if "get_child" in dir(self):
        return [self.get_child()] if self.get_child() else []

    children = []
    child = self.get_first_child()

    while child:
        children.append(child)
        child = child.get_next_sibling()

    return children

def _set_children(self, children):
    children = map(lambda x: x if isinstance(x, Gtk.Widget) else Gtk.Label(visible=True, label=x), children)

    for child in children:
        add_child(self, _builder, child)

def astalify(widget: Gtk.Widget, config=None):
    if config == None:
        config = {}

    class Widget(widget):
        __gtype_name__ = "AstalPy" + widget.__name__
        class_name = ''
        no_implicit_destroy = False

        def hook(self, object: GObject.Object, signal_or_callback: str | Callable, callback: Callable = lambda _, x: x):
            if isinstance(signal_or_callback, Callable):
                callback = signal_or_callback

            if isinstance(object, Variable):
                unsubscribe = object.subscribe(callback)

            else:
                if isinstance(signal_or_callback, Callable): return 

                if 'notify::' in signal_or_callback:
                    id = object.connect(
                        f'{signal_or_callback}', 
                        lambda *_: callback(
                            self, 
                            object.get_property(signal_or_callback.replace('notify::', '').replace('-', '_'))))

                else:
                    id = object.connect(
                        signal_or_callback, 
                        lambda _, value, *args: callback(self, value) if not args else callback(self, value, *args))

                unsubscribe = lambda *_: object.disconnect(id)

            self.connect('destroy', unsubscribe)
        
        def toggle_class_name(self, name: str, state: bool | None = None):
            if state == None:
                if name in self.get_css_classes():
                    self.remove_css_class(name)

                else:
                    self.add_css_class(name)

            else:
                if state:
                    self.add_css_class(name)

                else:
                    self.remove_css_class(name)

        @GObject.Property(type=str)
        def class_name(self):
            return ' '.join(self.get_css_classes())

        @class_name.setter
        def class_name(self, name):
            self.set_css_classes(name.split(' '))

        # @GObject.Property(type=str)
        # def css(self):
        #     return Astal.widget_get_css(self)

        # @css.setter
        # def css(self, css: str):
        #     Astal.widget_set_css(self, css)

        @GObject.Property(type=str)
        def cursor(self):
            return Astal.widget_get_cursor(self)

        @cursor.setter
        def cursor(self, cursor: str):
            Astal.widget_set_cursor(self, cursor)

        @GObject.Property(type=str)
        def click_through(self):
            return Astal.widget_get_click_through(self)
       
        @click_through.setter
        def click_through(self, click_through: str):
            Astal.widget_set_click_through(self, click_through)

        @GObject.Property()
        def children(self):
            return _get_children(self)

        @children.setter
        def children(self, children):
            for child in _get_children(self):
                if isinstance(child, Gtk.Widget):
                    child.unparent()
                    if not child in children:
                        child.run_dispose()

            return config.get("set_children", _set_children)(self, children)

        def __init__(self, **props):
            super().__init__()

            self.set_visible(props.get("visible", True))

            props = setup_controllers(self, **props)

            for prop, value in props.items():
                if isinstance(value, Binding):
                    self.set_property(prop, value.get())
                    unsubscribe = value.subscribe(partial(self.set_property, prop))
                    self.connect('destroy', unsubscribe)

                elif 'on_' == prop[0:3] and isinstance(value, Callable):
                    self.connect(prop.replace('on_', '', 1), value) 

                elif prop.replace('_', '-') in map(lambda x: x.name, self.props):
                    self.set_property(prop.replace('_', '-'), value)

                elif prop == 'setup' and isinstance(value, Callable):
                    value(self)

                elif prop == 'no_implicit_destroy':
                    self.no_implicit_destroy = True

                else:
                    self.__setattr__(prop, value)

    return Widget

def setup_controllers(
    widget,
    on_focus_enter=None,
    on_focus_leave=None,
    on_key_pressed=None,
    on_key_released=None,
    on_key_modifier=None,
    on_legacy=None,
    on_button_pressed=None,
    on_button_released=None,
    on_hover_enter=None,
    on_hover_leave=None,
    on_motion=None,
    on_scroll=None,
    on_scroll_decelerate=None,
    **props
):
    if on_focus_enter or on_focus_leave:
        focus = Gtk.EventControllerFocus()
        widget.add_controller(focus)

        if on_focus_enter:
            focus.connect('enter', lambda: on_focus_enter(widget))

        if on_focus_leave:
            focus.connect('leave', lambda: on_focus_leave(widget))

    if on_key_pressed or on_key_released or on_key_modifier:
        key = Gtk.EventControllerKey()
        widget.add_controller(key)

        if on_key_pressed:
            key.connect('key-pressed', lambda _, val, code, state: on_key_pressed(widget, val, code, state))

        if on_key_released:
            key.connect('key-released', lambda _, val, code, state: on_key_released(widget, val, code, state))

        if on_key_modifier:
            key.connect('key-modifier', lambda _, val, code, state: on_key_modifier(widget, val, code, state))

    if on_legacy or on_key_released or on_key_modifier:
        legacy = Gtk.EventControllerLegacy()
        widget.add_controller(legacy)

        def callback(_, event):
            if event.get_event_type() == Gdk.EventType.BUTTON_PRESS:
                on_button_pressed(widget, event) if on_button_pressed else ...

            if event.get_event_type() == Gdk.EventType.BUTTON_PRESS:
                on_button_released(widget, event) if on_button_released else ...

            on_legacy(widget, event) if on_legacy else ...

        legacy.connect('event', callback)

    if on_hover_enter or on_hover_leave or on_motion:
        motion = Gtk.EventControllerMotion()
        widget.add_controller(motion)

        if on_hover_enter:
            motion.connect('enter', lambda _, x, y: on_hover_enter(widget, x, y))

        if on_hover_leave:
            motion.connect('leave', lambda: on_hover_leave(widget))

        if on_motion:
            motion.connect('motion', lambda _, x, y: on_motion(widget, x, y))

    if on_scroll or on_scroll_decelerate:
        scroll = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.BOTH_AXIS | Gtk.EventControllerScroll.KINETIC)
        widget.add_controller(scroll)

        if on_scroll:
            scroll.connect('scroll', lambda _, x, y: on_scroll(widget, x, y))

        if on_scroll_decelerate:
            scroll.connect('scroll', lambda _, x, y: on_scroll_decelerate(widget, x, y))

    return props
