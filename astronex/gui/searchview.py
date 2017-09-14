# -*- coding: utf-8 -*-
import gtk, gobject
import re, time


class SearchView(gtk.TreeView):
    def __init__(self,model):
        gtk.TreeView.__init__(self,model)
        self.set_enable_search(False)
        self.connect('start-interactive-search', self.on_search_start)
        self.connect('button-press-event', self.on_buttonpress)
        self.connect('key-press-event', self.on_keypress)
        self.searchbox_on = False
        self.search_win = None
        self.start_time = 0

    def on_search_start(self,view):
        if not self.searchbox_on:
            self.interactive_search(view)

    def interactive_search(self,view,key=''):
        self.searchbox_on = True
        search_win = gtk.Window()
        vbox = gtk.VBox()
        search_win.add(vbox)
        search_win.set_modal(False)
        search_win.set_decorated(False)
        self.search_win = search_win

        frame = gtk.Frame()
        vbox.pack_start(frame,False,False)
        search_entry = gtk.Entry()
        frame.add(search_entry)
        search_entry.connect('key-press-event', self.on_entry_keypress)
        search_entry.connect('button-press-event', self.on_entry_buttonpress)

        view.set_search_entry(search_entry)
        view.set_search_column(0)
        search_entry.set_text(key) 

        search_win.show_all()
        self.set_searchwin_pos(search_entry)
        search_entry.set_position(-1)

        self.start_time =  time.time()
        self.timeout_handle = gobject.timeout_add(1000,self.check_idle)

    def on_entry_keypress(self,entry,event):
        if event.keyval == gtk.keysyms.Return or event.keyval == gtk.keysyms.Escape:
            self.destroy_searchwin()
        return False; 

    def on_buttonpress(self,view,event):
        if self.searchbox_on:
            self.destroy_searchwin()

    def destroy_searchwin(self):
        self.set_search_entry(None)
        self.search_win.destroy()
        self.searchbox_on = False
        self.grab_focus()

    def set_searchwin_pos(self,search_entry):
        parent = self.parent
        while not isinstance(parent,gtk.Window):
            parent = parent.parent
        win_pos = parent.pos_x, parent.pos_y
        x = win_pos[0] + self.allocation.width - search_entry.allocation.width 
        y = win_pos[1] + self.allocation.height + self.allocation.y 
        self.search_win.move(x,y)


    def on_keypress(self,view,event): 
        if (event.keyval > 255 or event.keyval < 32):
            return False 
        if (event.state & gtk.gdk.CONTROL_MASK):
            return False
        if (re.match('[a-zA-Z\s]', chr(event.keyval))):
            self.interactive_search(view, chr(event.keyval))
            return True    
        return False

    def on_entry_buttonpress(self,entry,event):
        self.start_time = time.time()

    def check_idle(self):
        elapsed_time = time.time() -self.start_time
        if (elapsed_time > 3):
            gobject.source_remove(self.timeout_handle)
            self.destroy_searchwin()
            return False
        else:
            return True

