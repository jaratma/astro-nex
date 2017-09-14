# -*- coding: utf-8 -*-
import gtk
from .. extensions.ipython_view import IPythonView
import pango

import platform
if platform.system()=="Windows":
        FONT = "Lucida Console 9"
else:
        FONT = "Luxi Mono 10"

class ShellDialog(gtk.Window):
    def __init__(self,manager):
        gtk.Window.__init__(self)
        self.set_size_request(600,550)
        self.set_resizable(True)
        S = gtk.ScrolledWindow()
        S.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        V = IPythonView()
        V.modify_font(pango.FontDescription(FONT))
        V.set_wrap_mode(gtk.WRAP_CHAR)
        V.updateNamespace({'boss': manager})
        V.show()
        S.add(V)
        S.show()
        self.add(S)
        self.show()
        self.connect('delete_event',lambda x,y:False)
        #self.connect('destroy',lambda x:gtk.main_quit())
