# -*- coding: utf-8 -*-
import gtk
import sys,os,re
import pickle 
from datewidget import DateEntry, set_background
from pytz import timezone
from datetime import datetime
from .. extensions.validation import MaskEntry,ValidationError
from .. extensions.path import path

curr = None
boss = None
regex = re.compile("[A-Za-z][_A-Za-z0-9]*$")

class CouplesPanel(gtk.HBox):
    
    def __init__(self,parent):
        global curr,boss
        boss = parent.boss
        curr = boss.get_state()
        gtk.HBox.__init__(self)
        self.data = {'ftab':'','mtab':'','fname':'','mname':'','fid':None,'mid':None}
        self.changes = False
        self.coup_ix = 0

        hbox = gtk.HBox()
        vbox = gtk.VBox() 
        vbox.set_border_width(3) 
        vbox.set_size_request(400,-1)
        
        button = gtk.Button(_('Crear pareja'))
        button.connect('clicked',self.on_createcouple_clicked)
        vbox.pack_start(button,False,False)

        coupmodel = gtk.ListStore(str,str,int,str,str,int)
        coupview = gtk.TreeView(coupmodel)
        for c in curr.couples:
            coupmodel.append([c['fem'][0],c['fem'][1],c['fem'][2],
                c['mas'][0],c['mas'][1], c['mas'][2]])
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None,cell,text=0)
        coupview.append_column(column) 
        column = gtk.TreeViewColumn(None,cell,text=3)
        coupview.append_column(column) 
        sel = coupview.get_selection()
        sel.set_mode(gtk.SELECTION_SINGLE)
        sel.connect('changed',self.on_sel_changed)
        sel.select_path(0,)
        menu = gtk.Menu()
        menu_item = gtk.MenuItem(_('Eliminar'))
        menu.append(menu_item)
        menu_item.set_data('op','delete')
        menu_item.connect("activate", self.on_menuitem_activate)
        coupview.connect("button_press_event", self.on_view_clicked,menu)
        menu_item.show()
        vbox.pack_start(coupview,False,False)
        
        hbox.pack_start(vbox,True,True)
        hbox.pack_start(gtk.VSeparator(),False,False)
        
        vbox = gtk.VBox() 
        vbox.set_border_width(3) 
        vbox.set_size_request(400,-1)
        datewid = CoupleDates(self,boss)
        dt = datetime.now()
        tz = timezone('UTC')
        ld = tz.localize(dt)
        datewid.set_date(ld.date())
        bbox = gtk.Alignment(0.5,0,0,0)
        bbox.add(datewid)
        vbox.pack_start(bbox,False,False)
        but = gtk.Button()
        img = gtk.Image()
        appath = boss.app.appath
        imgfile = path.joinpath(appath,"astronex/resources/gtk-go-down.png")
        img.set_from_file(str(imgfile))
        but.set_image(img)
        but.connect('clicked',self.on_add_date_clicked)
        bbox = gtk.Alignment(0.5,0,0,0)
        bbox.add(but) 
        vbox.pack_start(bbox,False,False)
        
        datemodel = gtk.ListStore(str,str)
        dateview = gtk.TreeView(datemodel)
        dateview.set_headers_visible(False)
        dateview.set_size_request(-1,300)
        if curr.couples:
            for d in curr.couples[0]['dates']:
                datemodel.append([d[0],d[1]])
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None,cell,text=0)
        dateview.append_column(column) 
        cell = gtk.CellRendererText()
        cell.set_property('editable',True)
        cell.connect('edited', self.on_cell_edited)
        column = gtk.TreeViewColumn(None,cell,text=1)
        dateview.append_column(column) 
        sel = dateview.get_selection()
        sel.set_mode(gtk.SELECTION_SINGLE)
        sel.select_path(0,)
        menu = gtk.Menu()
        menu_item = gtk.MenuItem(_('Eliminar'))
        menu.append(menu_item)
        menu_item.connect("activate", self.on_menudate_activate)
        dateview.connect("button_press_event", self.on_dateview_clicked,menu)
        menu_item.show()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(dateview)
        vbox.pack_start(sw,False,False)
        
        hbox.pack_start(vbox,True,True)
        frame = gtk.Frame()
        frame.add(hbox)
        frame.set_border_width(6)
        self.pack_start(frame,False,False)
        
        self.coupview = coupview
        self.datewid = datewid
        self.dateview = dateview
        datewid.view = dateview

    def on_createcouple_clicked(self,button): 
        dialog = gtk.Dialog(_("Crear pareja"), None,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_NONE,
                    gtk.STOCK_OK, gtk.RESPONSE_OK))
        hbox = gtk.HBox()
        hbox.pack_start(self.make_tables_selector('f'), True, True)
        hbox.pack_end(self.make_tables_selector('m'), True, True)
        dialog.vbox.pack_start(hbox, True, True)
        dialog.connect("response", self.create_response)
        dialog.show_all()

    def make_tables_selector(self,key): 
        vbox = gtk.VBox()        
        liststore = gtk.ListStore(str)
        tables = gtk.ComboBoxEntry(liststore)
        tables.set_size_request(182,-1)
        tables.get_children()[0].set_editable(False)
        cell = gtk.CellRendererText()
        tables.pack_start(cell)
        tablelist = curr.datab.get_databases()
        
        for c in tablelist:
            liststore.append([c])
        index = 0
        for i,r in enumerate(liststore):
            if r[0] == curr.database:
                index = i
                break 
        tables.set_active(index) 
        table = tables.get_active_text()
        self.data["%stab" % key] = table
        
        vbox.pack_start(tables,False,False)

        chartmodel = gtk.ListStore(str,int)
        personae = gtk.ComboBoxEntry(chartmodel)
        chartlist = curr.datab.get_chartlist(tables.get_active_text())

        for c in chartlist:
            glue = ", "
            if c[2] == '':  glue = ''
            chartmodel.append([c[2]+glue+c[1],int(c[0])])
        
        
        cell = gtk.CellRendererText()
        personae.pack_start(cell,True)
        personae.add_attribute(cell,'text',0)
        personae.set_size_request(100,28)
        personae.set_active(0)
        personae.connect('changed',self.on_persona_changed,key)
        personae.emit('changed')
        vbox.pack_start(personae,True,True) 
        vbox.set_size_request(210,-1)
        tables.connect('changed',self.on_tables_changed,personae,key)
        
        compl = gtk.EntryCompletion()
        compl.set_text_column(0)
        compl.set_model(personae.get_model())
        personae.child.set_completion(compl)
        compl.connect('match_selected', self.on_person_match,personae)
        
        return vbox
    
    def on_person_match(self,compl,model,iter,personae):
        sel = unicode(model.get_value(iter,0),"utf-8")
        for r in personae.get_model():
            if r[0] == sel:
                personae.set_active_iter(r.iter)
                break
    
    def on_persona_changed(self,combo,key):
        if combo.get_active() == -1: return
        model = combo.get_model()
        iter =  combo.get_active_iter()
        name = model.get_value(iter,0)
        try:
            last,first = name.split(',')
            name = first[1:]+" "+last
        except ValueError:
            pass
        id = model.get_value(iter,1)
        self.data["%sname" % key] = name
        self.data["%sid" % key] = id

    def on_tables_changed(self,combo,personae,key): 
        if combo.get_active() == -1: 
            return
        if personae:
            chartmodel = gtk.ListStore(str,int)
            table = combo.get_active_text()
            chartlist = curr.datab.get_chartlist(table) 
            for c in chartlist:
                glue = ", "
                if not c[2]:  glue = ''
                chartmodel.append([c[2]+glue+c[1] , int(c[0]) ])
            personae.set_model(chartmodel)
            personae.set_active(0)
            self.data["%stab" % key] = table
    
    def create_response(self,dialog,rid):
        if rid == gtk.RESPONSE_NONE or rid == gtk.RESPONSE_DELETE_EVENT:
            self.changes = False
            dialog.destroy()
            return
        couple = { 'fem': (self.data['fname'],self.data['ftab'],self.data['fid']),
                'mas': (self.data['mname'],self.data['mtab'],self.data['mid']),
                'dates': [] }
        curr.couples.append(couple)
        coupmodel = gtk.ListStore(str,str,int,str,str,int)
        for c in curr.couples:
            coupmodel.append([c['fem'][0],c['fem'][1],c['fem'][2],
                c['mas'][0],c['mas'][1], c['mas'][2]])
        self.coupview.set_model(coupmodel)
        self.coupview.get_selection().select_path(len(coupmodel)-1,) 
        self.changes = True
        dialog.destroy()

    def save_couples(self):
        if self.changes:
            curr.save_couples(boss.app)

    def on_view_clicked(self,view, event,menu):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            x = int(event.x)
            y = int(event.y)
            pthinfo = view.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                view.grab_focus()
                view.set_cursor(path,col,0)
                menu.popup(None, None, None, event.button, event.time)
            return True

    def on_sel_changed(self,sel):
        model, iter = sel.get_selected()
        if not iter:
            return
        self.coup_ix = model.get_path(iter)[0]
        datemodel = gtk.ListStore(str,str)
        for d in curr.couples[self.coup_ix]['dates']:
            datemodel.append([d[0],d[1]])
        try:
            self.dateview.set_model(datemodel)
        except AttributeError:
            pass

    def on_menuitem_activate(self,menuitem): 
        model,iter = self.coupview.get_selection().get_selected()
        i =  model.get_path(iter)[0]
        del curr.couples[i]
        model.remove(iter)
        if i >= 1:
            self.coupview.get_selection().select_path(i-1,) 
        elif len(model) == 1:
            self.coupview.get_selection().select_path(0,) 
        else:
            datemodel = gtk.ListStore(str,str)
            self.dateview.set_model(datemodel) 
        self.changes = True

    def on_menudate_activate(self,menuitem): 
        model,iter = self.dateview.get_selection().get_selected()
        i =  model.get_path(iter)[0]
        model.remove(iter)
        del curr.couples[self.coup_ix]['dates'][i]
        self.changes = True

    def on_dateview_clicked(self,view, event,menu):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            x = int(event.x)
            y = int(event.y)
            pthinfo = view.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                view.grab_focus()
                view.set_cursor(path,col,0)
                menu.popup(None, None, None, event.button, event.time)
            return True

    def on_cell_edited(self,cell,path_string,newtext):
        model = self.dateview.get_model()
        iter = model.get_iter_from_string(path_string)
        path = model.get_path(iter)[0] 
        date = model.get_value(iter, 0)
        curr.couples[self.coup_ix]['dates'][path] = (date,newtext)
        ntxt = curr.couples[self.coup_ix]['dates'][path][1]
        model.set_value(iter, 1, ntxt)
        self.changes = True 

    def on_add_date_clicked(self,but):
        if  len(self.coupview.get_model()) < 1:
            return
        date = self.datewid.date
        dtstring = str(date.day) + "/" + str(date.month) + "/" + str(date.year)
        model = self.dateview.get_model()
        iter = model.append()
        desc = _('Acontecimiento')
        model.set(iter,0,dtstring,1,desc)
        curr.couples[self.coup_ix]['dates'].append((dtstring,desc))
        self.changes = True
        

class CoupleDates(DateEntry):
    def __init__(self,parent,boss):
        self.container = parent
        DateEntry.__init__(self,boss,fullpanel=False)
        self.view = None

    def calc_and_set(self,entry):
        try:
            self.date = self.get_date()
            set_background(entry, "#ffffff") 
        except ValidationError, e:
            self.date = None
            set_background(entry, "#ff699a")
        if self.date is None: 
            return
        try:
            model, iter = self.view.get_selection().get_selected()
            if iter:
                date = self.date
                dtstring = str(date.day) + "/" + str(date.month) + "/" + str(date.year)
                model.set(iter, 0, dtstring)
                path = model.get_path(iter)[0] 
                desc = model.get_value(iter, 1)
                coup = self.container.coup_ix
                curr.couples[coup]['dates'][path] = (dtstring,desc)
                self.container.changes = True
        except AttributeError:
            pass
