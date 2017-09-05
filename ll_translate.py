#!/usr/bin/python
#-*- coding: utf-8 -*-

import gtk
import requests
import os
import json
import urllib
import time

def getText(intext):
    htext = urllib.quote_plus(intext)
    resp = requests.get("http://api.lingualeo.com/gettranslates?word=" + htext)
    try:
        resp = json.loads(resp.text)
    except BaseException:
        return "Error in parsing JSON data."
    res = ""
    ts = resp['translate']
    for t in ts:
        if "value" in t.keys() and t['value']:
            res += "- " + str(t['value']) + "\n"
    if not res: res = "No translation was found"
    res = "<span font='15' color='#294369'><tt>" + res + "</tt></span>"
    if "transcription" in resp.keys():
        transcription = resp['transcription']
    res = "<span font='13'>  </span><span font='15' color='#9e9e9e'>[" + transcription + "]</span>\n" + res
    return res

class PyApp(gtk.Window):
    def __init__(self):
        super(PyApp, self).__init__()
        htext = os.popen('xsel -o').read()

        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(8)
        self.set_geometry_hints(min_width=300, min_height=150)
        self.connect("destroy", gtk.main_quit)
        self.connect("focus_out_event", gtk.main_quit)
        self.set_title(htext)
        #self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NOTIFICATION)

        # Create an EventBox and add it to our toplevel window
        event_box = gtk.EventBox()
        self.add(event_box)
        event_box.show()

        text = getText(htext)
        label = gtk.Label()
        label.set_markup(text)
        #label.set_size_request(300, -1)
        #label.set_justify(gtk.JUSTIFY_CENTER)
        event_box.add(label) #self.add(label)
        # And bind an action to it
        #event_box.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.FOCUS_CHANGE_MASK)
        event_box.connect("button_press_event", lambda w,e: gtk.main_quit())

        # More things you need an X window for ...
        event_box.realize()
        #event_box.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))

        # Set background color to green
        #event_box.modify_bg(gtk.STATE_NORMAL, event_box.get_colormap().alloc_color("grey"))

        self.show_all()

def main():
    PyApp()
    gtk.main()

if __name__ == '__main__':
    main()