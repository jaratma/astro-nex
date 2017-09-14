# -*- coding: utf-8 -*-
import gtk
from .. countries import cata_reg
from .. boss import boss
from searchview import SearchView
curr = boss.get_state()

def filter_region(model,iter,code):
    value = model.get_value(iter,1)
    return value == code 

class LocWidget(gtk.VBox):
    def __init__(self,default=False):
        gtk.VBox.__init__(self)
        self.set_homogeneous(False)

        if not default:
            if curr.usa:
                x,c = curr.loc.region.split('(')
                c = curr.datab.get_usacode_from_name(c[:-1])
                country_code = c
            else:
                country_code = curr.loc.country_code
            region = curr.loc.region_code
            city = curr.loc.city 
        else:
            curr.usa = {'false':False,'true':True}[boss.opts.usa]
            country_code = boss.opts.country
            region = boss.opts.region
            city = boss.opts.locality
            curr.country = country_code

        self.countries = curr.datab.get_states_tuple(curr.usa)
        self.sortlist = sorted(self.countries) 

        compl = gtk.EntryCompletion()
        # country label and check btns 
        hbox = gtk.HBox()
        l = [_('Pais'),_('Estado')][curr.usa]
        label = gtk.Label(l)
        hbox.pack_start(label,False,False)
        self.check = gtk.CheckButton(_("Usa"))
        self.check.set_active(curr.usa)
        self.check.connect('toggled',self.on_usa_toggled,compl,label)
        hbox.pack_start(self.check,True,False)
        
        self.filtcheck = gtk.CheckButton(_("Filtro"))
        self.filtcheck.connect('toggled',self.on_filter_toggled)
        hbox.pack_start(self.filtcheck,True,False) 
        label = gtk.Label(_('Region'))
        hbox.pack_end(label,True,False)
        hbox.set_border_width(3) 
        hbox.set_homogeneous(True) 
        self.pack_start(hbox,False,False)

        # country combo
        hbox = gtk.HBox()
        liststore = gtk.ListStore(str,str)
        self.country_combo = gtk.ComboBoxEntry(liststore)
        cell = gtk.CellRendererText()
        self.country_combo.pack_start(cell)
        
        for n,c in self.sortlist:
            liststore.append([n,c])

        for r in self.country_combo.get_model():
            if r[1] == country_code:
                self.country_combo.set_active_iter(r.iter)
                break
        
        compl.set_text_column(0)
        compl.set_model(self.country_combo.get_model())
        self.country_combo.child.set_completion(compl)#entry
        compl.connect('match_selected', self.on_count_match)

        self.country_combo.set_wrap_width(4)
        self.country_combo.connect('changed',self.on_count_selected) 
        hbox.pack_start(self.country_combo,False,False)

        
        # region combo
        liststore = gtk.ListStore(str,str)
        self.reg_combo = gtk.ComboBoxEntry(liststore)
        cell = gtk.CellRendererText()
        self.reg_combo.pack_start(cell)
        self.reg_combo.connect('changed',self.on_reg_selected)
        rlist = curr.datab.list_regions(country_code,curr.usa)
        if country_code == u"SP" and boss.opts.lang == 'ca':
            temp = []
            for r in rlist:
                temp.append((cata_reg[r[0]],r[1]))
            rlist = temp

        i = 0
        for n,r in enumerate(rlist):
            liststore.append(r)
            if region == r[1]:
                i = n

        self.reg_combo.set_active(i)
        hbox.pack_end(self.reg_combo,False,False)
        self.pack_start(hbox,False,False)

        # locality view
        self.locmodel = gtk.ListStore(str,str,str)
        #self.locview = gtk.TreeView(self.locmodel)
        self.locview = SearchView(self.locmodel)
        selection = self.locview.get_selection()
        selection.connect('changed',self.on_sel_changed)
        selection.set_mode(gtk.SELECTION_SINGLE)
        loclist = curr.datab.fetch_all_from_country(country_code,curr.usa)
        i = 0
        for n,c in enumerate(loclist):
            self.locmodel.append(c)
            if city == c[0]:
                i = n

        cell = gtk.CellRendererText()
        cell.set_property('width-chars',38)
        cell.set_property('foreground','blue')
        cellgeo = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None)
        column.pack_start(cell,False)
        column.pack_start(cellgeo,False)
        column.set_attributes(cell,text=0)
        column.set_attributes(cellgeo,text=2)
        column.set_widget(gtk.HSeparator())
        self.locview.append_column(column) 
        self.locview.set_headers_visible(False)
        #self.locview.set_enable_search(True)
        self.locview.set_cursor(i,column)
        self.locview.scroll_to_cell(i)
        self.locview.connect('row-activated',self.on_row_activate)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.locview) 
        self.pack_start(sw)


    def on_reg_selected(self,combo):
        model = combo.get_model()
        active = combo.get_active()
        if active < 0: 
            return
        self.reg_code = model[active][1]
        if self.filtcheck.get_active():
            filtmodel = self.locmodel.filter_new()
            filtmodel.set_visible_func(filter_region, self.reg_code)
            self.locview.set_model(filtmodel)

    def on_count_selected(self,combo):
        iter = combo.get_active_iter()
        if not iter: return
        model = combo.get_model()
        code = unicode(model.get_value(iter,1),"utf-8")
        liststore = gtk.ListStore(str,str)
        rlist = curr.datab.list_regions(code,curr.usa)
        for r in rlist:
            liststore.append(r)
        self.reg_combo.set_model(liststore)
        self.reg_combo.set_active(0) 
        liststore = gtk.ListStore(str,str,str)
        loclist = curr.datab.fetch_all_from_country(code,curr.usa)
        for c in loclist:
            liststore.append(c)
        self.locview.set_model(liststore)
        self.locmodel = liststore
        self.set_country_code(code)

    def set_country_code(self,code):
        curr.country = code 

    def on_count_match(self,compl,model,iter):
        sel = unicode(model.get_value(iter,0),"utf-8")
        for r in self.country_combo.get_model():
            if r[0] == sel:
                self.country_combo.set_active_iter(r.iter)
                break

    def on_usa_toggled(self,check,cpl,lbl):
        if check.get_active():
            curr.usa = True
            lbl.set_text(_("Estado"))
        else:
            curr.usa = False
            lbl.set_text(_("Pais"))
        self.countries = curr.datab.get_states_tuple(curr.usa)
        self.sortlist = sorted(self.countries)
        model = gtk.ListStore(str,str)
        for n,c in self.sortlist:
            model.append([n,c])
        self.country_combo.set_model(model)
        cpl.set_model(model)
        for r in model:
            if r[1] == boss.opts.country:
                self.country_combo.set_active_iter(r.iter)
                break
        else:
            self.country_combo.set_active(0)

    def on_filter_toggled(self,check):
        if check.get_active():
            filtmodel = self.locmodel.filter_new()
            filtmodel.set_visible_func(filter_region, self.reg_code)
            self.locview.set_model(filtmodel)
        else:
            self.locview.set_model(self.locmodel)
        self.locview.get_selection().select_path("0")

    def on_row_activate(self,tree,path,col):
        model,iter = tree.get_selection().get_selected()
        city,code= model.get(iter,0,1)
        self.actualize_if_needed(city,code)

    def on_sel_changed(self,sel):
        model,iter = sel.get_selected()
        if not iter: return
        city,code= model.get(iter,0,1)
        for r in self.reg_combo.get_model():
            if code== r[1]:
                self.reg_combo.set_active_iter(r.iter)
                break
        self.actualize_if_needed(city,code)
        
    def actualize_if_needed(self,city,code):
        curr.setloc(city,code)
        if curr.curr_chart == curr.now:
            curr.set_now()
        if curr.curr_op == 'draw_local' or boss.mainwin.locselflag: 
            boss.da.redraw()
        else:
            active = boss.mpanel.active_slot
            curr.setchart()
            curr.act_pool(active,curr.calc)

    def set_default_local(self): 
        usa = boss.opts.usa
        usa = {'false':False,'true':True}[boss.opts.usa]
        if usa != self.check.get_active():
            self.check.set_active(usa)
            return
        self.countries = curr.datab.get_states_tuple(usa)
        self.sortlist = sorted(self.countries)
        model = gtk.ListStore(str,str)
        for n,c in self.sortlist:
            model.append([n,c])
        self.country_combo.set_model(model)
        
        for r in model:
            if r[1] == boss.opts.country:
                self.country_combo.set_active_iter(r.iter)
                break
        else:
            self.country_combo.set_active(0)
        
        liststore = gtk.ListStore(str,str,str)
        loclist = curr.datab.fetch_all_from_country(boss.opts.country,usa)
        i = 0
        for n,c in enumerate(loclist):
            liststore.append(c)
            if boss.opts.locality == c[0]:
                i = n
        self.locview.set_model(liststore)
        self.locmodel = liststore
        self.locview.set_cursor(i)
        self.locview.scroll_to_cell(i)
