# -*- coding: utf-8 -*-
import gtk
from pytz import timezone
from datewidget import DateEntry
from localwidget import LocWidget
from datetime import datetime, time
from .. utils import parsestrtime
from .. extensions.path import path
from mainnb import Slot
from copy import copy
curr = None

class PersonTable(gtk.Table):
    def __init__(self,current):
        global curr
        curr = current
        gtk.Table.__init__(self,2,2)
        lbl = gtk.Label(_('Nombre:'))
        self.attach(lbl,0,1,0,1)
        lbl = gtk.Label(_('Apellidos:'))
        self.attach(lbl,0,1,1,2)
        self.first = gtk.Entry()
        self.first.connect('changed', self.on_changed,curr)
        self.attach(self.first,1,2,0,1)
        self.last = gtk.Entry()
        self.last.connect('changed', self.on_changed,curr)
        self.attach(self.last,1,2,1,2)
        self.set_border_width(3) 

    def on_changed(self,w,curr):
        if w is self.first:      
            curr.person.first = unicode(w.get_text(),"utf-8")           
        elif w is self.last:
            curr.person.last =  unicode(w.get_text(),"utf-8")

class EntryDlg(gtk.Dialog):
    '''New chart inputs dialog'''

    def __init__(self,parent,calc=False):
        global curr
        self.boss = parent.boss
        opts = self.boss.opts
        curr = self.boss.state
        curr.person.set_first(True)
        #self.usa = curr.usa
        appath = self.boss.app.appath
        self.last_loaded = None
        
        gtk.Dialog.__init__(self,
                _("Entradas"), parent,
                gtk.DIALOG_DESTROY_WITH_PARENT,
                ())
        self.connect('configure-event', self.on_configure_event) 

        self.set_size_request(400,580)
        self.vbox.set_border_width(3)
        
        if curr.curr_op != 'draw_local': 
            self.pframe = gtk.Frame(_("Personal"))
            self.pframe.set_border_width(3)
            self.pframe.add(PersonTable(curr))
            self.vbox.pack_start(self.pframe,False,False)
            
            dw = self.create_datewidget()
            self.vbox.pack_start(dw,False)
            self.dw = dw.child
        
        loc = self.create_locwidget()
        self.vbox.pack_start(loc)
        self.loc = loc.child 
        
        hbox = gtk.HBox()
        but = gtk.Button()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"astronex/resources/stock_refresh.png")
        img.set_from_file(str(imgfile))
        but.set_image(img)
        hbox.pack_start(but,False,False)
        but.connect('clicked',self.on_refesh_clicked)
        
        but = gtk.Button()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"astronex/resources/gtk-clear.png")
        img.set_from_file(str(imgfile))
        but.set_image(img)
        hbox.pack_start(but,False,False)
        but.connect('clicked',self.on_clear_clicked)
        
        but = gtk.Button()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"astronex/resources/gtk-cancel.png")
        img.set_from_file(str(imgfile))
        but.set_image(img)
        but.set_size_request(80,-1)
        but.connect("clicked", self.dlg_response,self,'cancel',parent)
        hbox.pack_end(but,False,False)
        
        but = gtk.Button()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"astronex/resources/gtk-save.png")
        img.set_from_file(str(imgfile))
        but.set_image(img)
        but.set_size_request(80,-1)
        but.connect("clicked", self.dlg_response,self,'save',parent)
        hbox.pack_end(but,False,False)
        self.vbox.pack_end(hbox,False,False)
        self.connect("response", self.quit_response,parent)
        self.show_all()
        
        wpos = self.window.get_position()
        self.pos_x = wpos[0]
        self.pos_y = wpos[1]

    def on_configure_event(self,widget,event):
        self.pos_x = event.x
        self.pos_y = event.y
    
    def quit_response(self,dialog,rid,parent):
        #curr.usa = self.usa
        main = self.boss.mpanel
        active = main.active_slot
        if curr.curr_chart.first == _('Momento actual'):
            chart = curr.now
        else:
            chart = curr.get_active(active)
            if not curr.is_valid(active):
                chart = curr.now
            self.boss.da.panel.nowbut.emit('clicked')
        main.actualize_pool(active,chart)
        parent.entry = None
        dialog.destroy()
        return

    def dlg_response(self,but,dialog,rid,parent):
        #curr.usa = self.usa
        main = self.boss.mpanel
        active = main.active_slot
        chart = curr.get_active(active)
        if rid == 'save':
            self.dw.timeentry.emit('changed')
            curr.setchart()
            id, table = main.browser.new_chart(curr.calc) 
            if id:
                curr.datab.load_chart(table,id,chart)
        if not curr.is_valid(active):
            chart = curr.now
        else:
            curr.add_to_pool(copy(chart),Slot.overwrite)
        main.actualize_pool(active,chart)
        self.boss.da.redraw()
        parent.entry = None
        self.boss.da.panel.nowbut.emit('clicked')
        dialog.destroy()
        return
    
    def create_datewidget(self):
        dw = DateEntry(self.boss)
        dt = datetime.now()
        tz = timezone('UTC')
        ld = tz.localize(dt)
        dw.set_date(ld.date())
        dw.set_time(ld.time())
        dw.set_border_width(3) 
        
        frame = gtk.Frame(_("Fecha y hora"))
        frame.set_border_width(3)
        frame.add(dw)
        return frame
   
    def create_locwidget(self):
        loc = LocWidget()
        frame = gtk.Frame(_("Localidad"))
        frame.set_border_width(3)
        frame.add(loc)
        return frame

    def modify_entries(self,chart): 
        self.last_loaded = chart
        if curr and curr.curr_op != 'draw_local': 
            table = self.pframe.child
            table.first.set_text(chart.first)
            table.last.set_text(chart.last)
            date,thistime = parsestrtime(chart.date)
            thistime = thistime.split(' ')[0]
            self.dw.set_date(datetime(*reversed(map(int,date.split('/')))))
            self.dw.set_time(time(*map(int,thistime.split(':'))))
        
        loc = self.loc 
        if chart.country == 'USA':
            if not loc.check.get_active():
                loc.check.set_active(True)
            ix = chart.region.index('(')
            reg,state = chart.region[:ix].strip(),chart.region[ix:] 
            state = state[1:-1]
        else: 
            if loc.check.get_active():
                loc.check.set_active(False)
            reg = chart.region
            state = t(chart.country)
        for r in loc.country_combo.get_model():
            if r[0] == state:
                loc.country_combo.set_active_iter(r.iter)
                break 
        loc.reg_combo.child.set_text(reg)
        
        model = loc.locview.get_model()
        iter = model.get_iter("0"); i = 0
        while iter:
            city = model.get(iter,0)[0] 
            if city == chart.city: break
            i +=1
            iter = model.iter_next(iter) 
        loc.locview.set_cursor(i)
        loc.locview.scroll_to_cell(i)

    def on_refesh_clicked(self,but):
        self.loc.set_default_local()

    def on_clear_clicked(self,but):
        if self.last_loaded:
            self.modify_entries(self.last_loaded)
        else:
            curr.set_now()
            self.modify_entries(curr.now)
