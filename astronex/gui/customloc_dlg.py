# -*- coding: utf-8 -*-
import gtk
import os
import re
from itertools import izip,count
from .. extensions.path import path
from .. extensions.validation import MaskEntry
from .. utils import degtodec 
from localwidget import LocWidget
from .. countries import cata_reg
from .. boss import boss 
curr = boss.get_state()
datab = boss.get_database()


class CustomLocDlg(gtk.Dialog):
    def __init__(self,boss):
        gtk.Dialog.__init__(self,
                _("Anadir localidad"), None,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                    (gtk.STOCK_SAVE, gtk.RESPONSE_OK,
                gtk.STOCK_CLOSE, gtk.RESPONSE_NONE))
        self.set_size_request(400,500)

        self.widget = CustomLocWidget(self)
        frame = gtk.Frame()
        frame.add(self.widget)
        self.vbox.pack_start(frame,False,False)
        
        hbox = gtk.HBox()
        but = gtk.Button(_('Eliminar entrada'))
        but.connect('clicked',self.on_delete_entry)
        hbox.pack_start(but,False,False)
        but = gtk.Button(_('Modificar entrada'))
        but.connect('clicked',self.on_modify_entry)
        hbox.pack_end(but,False,False)
        self.vbox.pack_start(hbox,False,False)
        self.vbox.pack_start(gtk.HSeparator(),False,False) 
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC) 
        view = self.make_browser()
        sw.add(view) 
        self.locview = view
        self.vbox.pack_start(sw,True,True)

        self.connect("response", self.dlg_response)
        self.set_response_sensitive(gtk.RESPONSE_OK,False)
        self.show_all()

    def dlg_response(self,dialog,rid):
        if rid == gtk.RESPONSE_OK:
            resp = self.widget.pack_response()
            datab.save_attached_loc(resp)
            locmodel = gtk.ListStore(str,str,str,str,str) 
            loclist = datab.fetch_all_from_custom() 
            for n,c in enumerate(loclist):
                locmodel.append(c)
            self.locview.set_model(locmodel)
        else: 
            dialog.destroy()
        return

    def on_delete_entry(self,but):
        model,iter = self.locview.get_selection().get_selected()
        if not iter: return
        result = self.deletedialog()
        if result == gtk.RESPONSE_OK:
            city = model.get_value(iter,0)
            code = model.get_value(iter,1)
            table = model.get_value(iter,3) 
            datab.delete_custom_loc(table,city,code)
            locmodel = gtk.ListStore(str,str,str,str,str) 
            loclist = datab.fetch_all_from_custom() 
            for n,c in enumerate(loclist):
                locmodel.append(c)
            self.locview.set_model(locmodel)

    def deletedialog(self):
        msg = [_("Eliminar una localidad puede impedir modificar "),
            _("luego una carta con facilidad. Continuar?")]
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_OK_CANCEL, "\n".join(msg))
        result = dialog.run()
        dialog.destroy()
        return result
    
    def on_modify_entry(self,but):
        model,iter = self.locview.get_selection().get_selected()
        if not iter: return
        city = model.get_value(iter,0)
        code = model.get_value(iter,1)
        geo = model.get_value(iter,2)
        table = model.get_value(iter,3) 
        count  = model.get_value(iter,4) 
        self.widget.locentry.set_text(city)
        self.widget.country_combo.child.set_text(count)
        long,lat = geo.split(' ')
        d,L,m = long.partition('E')
        if L == '':
            d,L,m = long.partition('W') 
        self.widget.gcombos[0].set_active(['E','W'].index(L))
        self.widget.gentries[0].set_text(".".join([d.rjust(3,'0'),m,'00']))
        L = ''
        d,L,m = lat.partition('N')
        if L == '':
            d,L,m = lat.partition('S') 
        self.widget.gcombos[1].set_active(['N','S'].index(L)) 
        self.widget.gentries[1].set_text(".".join([d,m,'00']))
        _, count = table.split('_')
        if count.startswith('US'):
            self.widget.check.set_active(True)
            reg = datab.get_usadistrict_from_code(count[2:],code)
        else:
            self.widget.check.set_active(False)
            reg = datab.get_regionname_from_code(count.upper(),code)
        model = self.widget.reg_combo.get_model()
        for r in model:
            if r[0] == reg:
                self.widget.reg_combo.set_active_iter(r.iter)
                break

    def make_browser(self):
        locmodel = gtk.ListStore(str,str,str,str,str)
        locview = gtk.TreeView(locmodel)
        selection = locview.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        loclist = datab.fetch_all_from_custom() 
        for n,c in enumerate(loclist):
            locmodel.append(c)

        cell = gtk.CellRendererText()
        cell.set_property('width-chars',26)
        cell.set_property('foreground','blue')
        cellgeo = gtk.CellRendererText()
        cellcount = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None)
        column.pack_start(cell,False)
        column.pack_start(cellgeo,False)
        column.pack_start(cellcount,False)
        column.set_attributes(cell,text=0)
        column.set_attributes(cellgeo,text=2)
        column.set_attributes(cellcount,text=4)
        column.set_widget(gtk.HSeparator())
        locview.append_column(column) 
        locview.set_headers_visible(False)
        #locview.connect('row-activated',self.on_row_activate)
        return locview
    
def filter_region(model,iter,code):
    value = model.get_value(iter,1)
    return value == code 

class CustomLocWidget(gtk.VBox):
    def __init__(self,dialog):
        gtk.VBox.__init__(self)
        self.set_homogeneous(False)
        self.dialog = dialog
        self.usa = False

        self.countries = datab.get_states()
        self.countrycode = curr.country
        compl = gtk.EntryCompletion()
        
        region = curr.loc.region
        city = curr.loc.city
        self.locmodel = None

        self.sortlist = sorted(self.countries.keys())
        revlist = dict((reversed(list(i)) for i in self.countries.items()))
        default = self.sortlist.index(revlist[self.countrycode])
        
        # country label and check btns 
        hbox = gtk.HBox()
        hbox.set_border_width(4)
        label1 = gtk.Label(_('Pais')+"      ")
        label2 = gtk.Label(_('Region'))
        hbox.pack_start(label1,False,False,padding=8)
        self.check = gtk.CheckButton("Usa")
        self.check.connect('toggled',self.on_usa_toggled,compl,default,label1)
        hbox.pack_start(self.check,False,False)
        hbox.pack_end(label2,False,False,padding=8)
        self.pack_start(hbox,False,False)

        # country combo
        hbox = gtk.HBox()
        hbox.set_border_width(6)
        liststore = gtk.ListStore(str)
        self.country_combo = gtk.ComboBoxEntry(liststore)
        cell = gtk.CellRendererText()
        self.country_combo.pack_start(cell)
        
        for c in self.sortlist:
            liststore.append([c])
        
        compl.set_text_column(0)
        compl.set_model(self.country_combo.get_model())
        entry = self.country_combo.child
        entry.set_completion(compl)
        compl.connect('match_selected', self.on_count_match)

        self.country_combo.set_active(default)
        self.country_combo.set_wrap_width(4)
        self.country_combo.connect('changed',self.on_count_selected)

        hbox.pack_start(self.country_combo,False,False)

        # region combo
        liststore = gtk.ListStore(str,str)
        self.reg_combo = gtk.ComboBoxEntry(liststore)
        cell = gtk.CellRendererText()
        self.reg_combo.pack_start(cell)
        self.reg_combo.connect('changed',self.on_reg_selected)
        rlist = datab.list_regions(self.countrycode)
        if self.countrycode == u"SP" and boss.opts.lang == 'ca':
            temp = []
            for r in rlist:
                temp.append((cata_reg[r[0]],r[1]))
            rlist = temp
        
        i = 0
        for n,r in enumerate(rlist):
            liststore.append(r)
            if region == r[0]:
                i = n

        self.reg_combo.set_active(i)
        hbox.pack_end(self.reg_combo,False,False)
        self.pack_start(hbox,False,False)

        # entries
        table= gtk.Table(3,3)
        table.set_border_width(6)
        table.set_col_spacings(6)
        label = gtk.Label(_("Localidad"))
        label.set_alignment(1.0,0.5)
        table.attach(label,0,1,0,1)
        label = gtk.Label(_("Longitud"))
        label.set_alignment(1.0,0.5)
        table.attach(label,0,1,1,2)
        label = gtk.Label(_("Latitud"))
        label.set_alignment(1.0,0.5)
        table.attach(label,0,1,2,3)

        locname = gtk.Entry()
        table.attach(locname,1,3,0,1)
        locname.connect('changed',self.on_locname_changed)
        self.locentry = locname
        
        self.gentries = []
        self.longdeg = "0"
        long = MaskEntry()
        long.set_mask("000.00.00")
        mask = long.get_mask()
        long.set_width_chars(len(mask))
        long.set_text("000.00.00")
        long.connect("changed",self.on_geoentry_changed,'long')
        table.attach(long,1,2,1,2)
        self.gentries.append(long)
        
        self.gcombos = []
        store = gtk.ListStore(str)
        store.append([_('E')])
        store.append([_('W')])
        combo = gtk.ComboBox(store)
        cell = gtk.CellRendererText()
        combo.pack_start(cell,True)
        combo.add_attribute(cell,'text',0)
        combo.set_size_request(40,-1)
        combo.connect('changed',self.on_geocombo_changed,'long')
        combo.set_active(0)
        self.longletter = ['E','W'][combo.get_active()]
        table.attach(combo,2,3,1,2)
        self.gcombos.append(combo)
        
        self.latdeg = "0"
        lat = MaskEntry()
        lat.set_mask("00.00.00")
        mask = lat.get_mask()
        lat.set_width_chars(len(mask))
        lat.set_text("00.00.00")
        lat.connect("changed",self.on_geoentry_changed,'lat')
        table.attach(lat,1,2,2,3)
        self.gentries.append(lat)

        store = gtk.ListStore(str)
        store.append([_('N')])
        store.append([_('S')])
        combo = gtk.ComboBox(store)
        cell = gtk.CellRendererText()
        combo.pack_start(cell,True)
        combo.add_attribute(cell,'text',0)
        combo.set_size_request(40,-1)
        combo.connect('changed',self.on_geocombo_changed,'lat')
        combo.set_active(0)
        self.latletter = ['N','S'][combo.get_active()]
        table.attach(combo,2,3,2,3)
        self.gcombos.append(combo)
        
        self.pack_start(table,False,False)


    def on_reg_selected(self,combo):
        model = combo.get_model()
        active = combo.get_active()
        self.reg_code = model[active][1]
        if self.locmodel:
            filtmodel = self.locmodel.filter_new()
            filtmodel.set_visible_func(filter_region, self.reg_code)
            if self.filtcheck.get_active():
                self.locview.set_model(filtmodel)

    def on_count_selected(self,combo):
        sel = unicode(combo.get_active_text(),"utf-8")
        try:
            code = self.countries[sel]
            liststore = gtk.ListStore(str,str)
            rlist = datab.list_regions(code,self.usa)
            for r in rlist:
                liststore.append(r)
            self.reg_combo.set_model(liststore)
            self.reg_combo.set_active(0) 
            self.set_country_code(code)
        except KeyError:
            pass

    def set_country_code(self,code):
            self.countrycode = code 

    def on_count_match(self,compl,model,iter):
        sel = unicode(model.get_value(iter,0),"utf-8")
        sl = self.sortlist
        self.country_combo.set_active(sl.index(sel))

    def on_usa_toggled(self,check,cpl,dfl,lbl):
        if check.get_active():
            self.usa = True
            self.countries = datab.get_states(True)
            default = 0
            lbl.set_text(_("Estado"))
        else:
            self.usa = False
            self.countries = datab.get_states()
            default = dfl
            lbl.set_text(_("Pais"))
        self.sortlist = sorted(self.countries.keys())
        model = gtk.ListStore(str)
        for c in self.sortlist:
            model.append([c])
        self.country_combo.set_model(model)
        cpl.set_model(model)
        self.country_combo.set_active(default)

    def on_geocombo_changed(self,combo,geo):
        if geo == 'long':
            self.longletter = ['E','W'][combo.get_active()]
        else:
            self.latletter = ['N','S'][combo.get_active()]

    def on_geoentry_changed(self,entry,geo):
        fields = entry.get_field_text()
        if None in fields: 
            return

        def pad(f,i):
            if i == 0 and geo == 'long':
                n = 3
            else:
                n = 2
            return str(f).rjust(n,'0')
        
        mayor = { 'long': 180, 'lat': 80 }
        mayor = { 'long': 180, 'lat': 80 }
        checks = [ mayor[geo], 60, 60 ]
        for i,fld in enumerate(fields):
            if fld and fld >= checks[i]:
                fields[i] = 0 
                wrongdeg = '.'.join((pad(f,i) for i,f in enumerate(fields)))
                entry.set_text(wrongdeg)
                
        if geo == "long":
            longdeg = ''.join((pad(f,i) for i,f in enumerate(fields)))
            self.longdeg = longdeg[:-1].lstrip('0') + longdeg[-1]
        else:
            latdeg = ''.join((pad(f,i) for i,f in enumerate(fields)))
            self.latdeg = latdeg[:-1].lstrip('0') + latdeg[-1]

    def on_locname_changed(self,entry):
        locname = entry.get_text()
        if not re.match("^\w(\w|-\s)*",locname, re.U):
            self.dialog.set_response_sensitive(gtk.RESPONSE_OK,False)
            entry.set_text("")
        else:
            self.locname = locname
            self.dialog.set_response_sensitive(gtk.RESPONSE_OK,True)

    def pack_response(self):
        if self.locname == "":
            return None
        
        if self.longletter == 'W' and self.longdeg != '0':
            self.longdeg = "-" + self.longdeg 
        if self.latletter == 'S' and self.latdeg != '0':
            self.latdeg = "-" + self.latdeg
        
        if self.usa:
            longdeg = degtodec(self.longdeg)
            latdeg = degtodec(self.latdeg)
        else:
            longdeg = self.longdeg
            latdeg = self.latdeg
        
        return self.countrycode, self.reg_code, self.locname, latdeg, longdeg, self.usa

