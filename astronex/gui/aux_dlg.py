# -*- coding: utf-8 -*-
import gtk
from .. surfaces.sdasurface import  DrawAux

class AuxWindow(gtk.Window):
    def __init__(self,parent,chart=None):
        self.boss = parent.boss
        gtk.Window.__init__(self)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        #self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_title("Astro-Nex")

        accel_group = gtk.AccelGroup()
        accel_group.connect_group(gtk.keysyms.Escape,0,gtk.ACCEL_LOCKED,self.escape)
        accel_group.connect_group(gtk.keysyms.plus,0,gtk.ACCEL_LOCKED,self.house_change)
        accel_group.connect_group(gtk.keysyms.minus,0,gtk.ACCEL_LOCKED,self.house_change)
        accel_group.connect_group(gtk.keysyms.Menu,0,gtk.ACCEL_LOCKED,self.popup_menu)
        accel_group.connect_group(gtk.keysyms.Up,gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.fake_scroll_up)
        accel_group.connect_group(gtk.keysyms.Down,gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.fake_scroll_down)
        self.add_accel_group(accel_group) 

        self.sda = DrawAux(self.boss,chart)
        self.add(self.sda)

        aux_size = int(self.boss.opts.aux_size)
        #self.set_size_request(450,450)
        self.set_default_size(aux_size,aux_size)
        self.connect('destroy', self.cb_exit,parent)
        self.show_all()

    def escape(self,a,b,c,d):
        self.destroy() 

    def cb_exit(self,e,parent):
        self.boss.da.auxwins.remove(self)
        return False
    
    def house_change(self,acgroup,actable,keyval,mod):
        #if self.boss.da.hselvisible:
        if  keyval == gtk.keysyms.plus:
            self.boss.da.hsel.child.house_updown(1)
        else:
            self.boss.da.hsel.child.house_updown(-1)

    def popup_menu(self,acgroup,actable,keyval,mod):
        self.sda.popup_menu()

    def fake_scroll_up(self,acgroup,actable,keyval,mod):
        event = gtk.gdk.Event(gtk.gdk.SCROLL)
        event.direction = gtk.gdk.SCROLL_UP
        self.sda.on_scroll(self.sda,event)
    
    def fake_scroll_down(self,acgroup,actable,keyval,mod):
        event = gtk.gdk.Event(gtk.gdk.SCROLL)
        event.direction = gtk.gdk.SCROLL_DOWN
        self.sda.on_scroll(self.sda,event)

