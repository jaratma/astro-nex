# -*- coding: utf-8 -*-
import sys,os
from copy import copy
from .. extensions.path import path
from .. countries import cata_reg
import gtk
import pango
import gobject
from .. utils import parsestrtime,format_longitud,format_latitud
import import_dlg
from oppanel import OpPanel
from searchview import SearchView
curr = None
boss = None

class Slot(gtk.VBox):
    overwrite = False
    storage = None
    def __init__(self,id):
        gtk.VBox.__init__(self)
        appath = boss.app.appath

        self.imgfile1 = path.joinpath(appath,"astronex/resources/stock_inbox-24.png")
        self.imgfile2 = path.joinpath(appath,"astronex/resources/gtk-folder-24.png")
        
        self.wname = id 
        self.chart_id = None
        self.timeout_sid = None
        names = ['master','click']
        names.remove(self.wname)
        self.other = names.pop()
        self.prev_clock_button = None
        self.prev_showpe = False
        self.swap = ['click','master']

        table = gtk.Table(4,2)
        hbutbox = gtk.HBox()
        but = gtk.Button()
        img = gtk.Image()
        if self.wname == 'master':
            img.set_from_file(str(self.imgfile1))
        else:
            img.set_from_file(str(self.imgfile2))
        but.set_image(img)
        but.connect('clicked',self.on_storage_clicked)
        hbutbox.pack_start(but,True,True)
        self.storage_img = img
        self.storage_but = but 
        table.attach(hbutbox,0,1,0,1)

        hbutbox = gtk.HBox()
        but = gtk.Button()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"astronex/resources/drivel-24.png")
        img.set_from_file(str(imgfile))
        but.set_image(img)
        but.connect('clicked',self.on_entry_clicked)
        self.mod = but
        but.set_tooltip_text(_('Modificar carta'))
        hbutbox.pack_end(but,False,False)
        but = gtk.Button()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"astronex/resources/clock-24.png")
        img.set_from_file(str(imgfile))
        but.set_image(img)
        but.connect('clicked',self.on_clock_clicked)
        self.clock = but
        but.set_tooltip_text(_('Carta del momento'))
        hbutbox.pack_end(but,False,False)
        ev = gtk.EventBox()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"astronex/resources/gnome-eog-24.png")
        img.set_from_file(str(imgfile))
        ev.add(img)        
        ev.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse("white"))
        hbutbox.pack_end(ev,True,True)
        ev.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        ev.connect("button_press_event",self.on_eye_clicked)
        self.eye = ev
        table.attach(hbutbox,1,2,0,1)

        self.namelbl = gtk.Label(_("Nombre"))
        self.namelbl.set_property('xalign',0.0)
        table.attach(self.namelbl,0,2,1,2)
        self.datelbl = gtk.Label(_("Fecha"))
        self.datelbl.set_property('xalign',0.0)
        table.attach(self.datelbl,0,2,2,3)
        self.loclbl = gtk.Label(_("Localidad"))
        self.loclbl.set_property('xalign',0.0)
        self.loclbl.set_ellipsize(pango.ELLIPSIZE_END)
        table.attach(self.loclbl,0,1,3,4)
        self.reglbl = gtk.Label(_("Region"))
        self.reglbl.set_property('xalign',0.0)
        self.reglbl.set_ellipsize(pango.ELLIPSIZE_END)
        table.attach(self.reglbl,1,2,3,4)
        table.set_border_width(2)
        eb = gtk.EventBox()
        eb.add(table)
        eb.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse("white"))

        self.pack_start(eb)
        self.eb = eb
        
        self.menu = gtk.Menu()
        for buf in (_('Exportar carta'),_('Importar carta')):
            menu_items = gtk.MenuItem(buf)
            self.menu.append(menu_items)
            menu_items.connect("activate", self.on_menuitem_activate)
            menu_items.show()
        self.connect("button_press_event", self.on_slot_clicked)
        self.connect('scroll-event', self.on_scroll_event)
        self.set_size_request(320,-1)

    def on_entry_clicked(self,but):
        #MainPanel.stop_timeout()
        if self.chart_id != 'now':
            widget = MainPanel.pool[self.wname]
            MainPanel.slot_activate(widget)
        chart = curr.charts[self.chart_id] 
        mainwin = boss.mainwin 
        if not mainwin.entry:
            mainwin.activate_entry()
        mainwin.entry.modify_entries(chart)

    def on_eye_clicked(self,eye,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            names = []
            for ch in curr.pool:
                names.append(" ".join([ch.first,ch.last]))
            menu = gtk.Menu()
            ow = gtk.CheckMenuItem(_('Sobrescribir'))
            ow.set_active(Slot.overwrite)
            ow.connect('toggled',self.on_ow_toggled)
            menu.append(ow)
            ow.show()
            sep_item = gtk.SeparatorMenuItem()
            menu.append(sep_item)
            sep_item.show()
            for i,ch in enumerate(curr.fav):
                name = (" ".join([ch.first,ch.last]))
                menu_item = gtk.MenuItem(name,False)
                menu.append(menu_item)
                menu_item.connect("activate", self.on_fav_menu_activate,menu,i)
                menu_item.show()
            if curr.fav:
                sep_item = gtk.SeparatorMenuItem()
                menu.append(sep_item)
                sep_item.show()
            for buf in names:
                menu_items = gtk.MenuItem(buf,False)
                menu.append(menu_items)
                menu_items.connect("activate", self.on_eye_menu_activate,menu)
                menu_items.show()
            menu.popup(None, None, None, 1, event.time)
            return True

    def on_ow_toggled(self,check):
        if check.get_active():
            Slot.overwrite = True
        else:
            Slot.overwrite = False

    def on_fav_menu_activate(self,menuitem,menu,ix):
        active = Slot.storage
        curr.load_from_fav(ix,active)
        MainPanel.actualize_pool(active,curr.charts[active]) 
        menu.popdown()  

    def on_eye_menu_activate(self,menuitem,menu):
        active = Slot.storage
        ix = 0
        name = menuitem.child.get_text()
        for i,ch in enumerate(list(curr.pool)):
            if " ".join([ch.first,ch.last]) == name:
                ix = i
                break
        #if curr.load_from_pool(ix,self.wname):
        if curr.load_from_pool(ix,active):
            MainPanel.actualize_pool(active,curr.charts[active]) 
        menu.popdown()  

    def on_clock_clicked(self,but):
        widget = MainPanel.pool[self.wname]
        MainPanel.slot_activate(widget)
        #boss.da.panel.nowbut.emit('clicked')
        MainPanel.actualize_pool(self.wname,curr.now)
        #if not boss.da.panelvisible:
        #    MainPanel.start_timeout()
        self.prev_clock_button = boss.mpanel.chooser.current_button
        boss.mpanel.chooser.init_button.emit('clicked')
        active = boss.mpanel.toolbar.get_nth_item(1).get_active()
        self.prev_showpe = active
        boss.mpanel.toolbar.get_nth_item(1).set_active(False) 
    
    def on_storage_clicked(self,but):
        other = MainPanel.pool[self.other]
        self.storage_img.set_from_file(str(self.imgfile1))
        other.storage_img.set_from_file(str(self.imgfile2)) 
        self.storage_but.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse("white"))
        other.storage_but.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse("#f6f7fe"))
        MainPanel.browser.slot = self.wname
        Slot.storage = self.wname

    def on_slot_clicked(self,slot,event):
        self.x,self.y = event.x,event.y
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.menu.popup(None, None, None, event.button, event.time)
            return True
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            if self.wname != MainPanel.active_slot:
                other = MainPanel.pool[self.other]
                self.eb.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse("white"))
                other.eb.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse("#f6f7fe"))
                self.eye.show()
                other.eye.hide() 
                curr.curr_chart,curr.curr_click = curr.curr_click,curr.curr_chart
                curr.crossed = not(curr.crossed)
                boss.redraw()
                boss.da.redraw_auxwins()
            elif self.chart_id == 'now':
                chart = curr.charts[self.wname]
                if curr.is_valid(chart.id):
                    MainPanel.actualize_pool(self.wname,chart) 
                try:
                  self.prev_clock_button.emit('clicked')
                except AttributeError:
                  pass
            MainPanel.active_slot = self.wname
            if self.chart_id == 'now':
                boss.mpanel.toolbar.get_nth_item(1).set_active(False)
            elif self.prev_showpe:
                boss.mpanel.toolbar.get_nth_item(1).set_active(True) 
            if boss.da.cycleselector:
                boss.da.cycleselector.refresh_spin()
            return True 
        return True

    def on_menuitem_activate(self,menuitem):
        if menuitem.child.get_text() == _('Exportar carta'):
            widget = MainPanel.pool[self.wname]
            MainPanel.slot_activate(widget)
            chart = curr.charts[self.chart_id] 
            if sys.platform == 'win32':
                import winshell
                folder = winshell.my_documents() + os.path.sep 
            else: 
                folder = os.path.expanduser("~") + os.path.sep
            name = "_".join((chart.first,chart.last)).strip().replace(" ","_")
            name = folder + name + ".nx1"
            file = open(name,'w')
            file.write(chart.__repr__())
            file.close()
        else:
            dialog = gtk.FileChooserDialog(_("Importar carta"), None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
            dialog.set_default_response(gtk.RESPONSE_OK)
            if sys.platform == 'win32':
                import winshell
                dialog.set_current_folder(winshell.my_documents())
            else: 
                dialog.set_current_folder(os.path.expanduser("~"))
            dialog.set_show_hidden(False)
            response = dialog.run()
            if response == gtk.RESPONSE_OK:
                filename = dialog.get_filename() 
                data = open(filename.decode('utf8')).read().split(",")
                chart = curr.charts[self.wname]
                try:
                    curr.load_import(chart,data)
                    MainPanel.actualize_pool(self.wname,chart) 
                except:
                    msg = _('Error importando carta')
                    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                            gtk.MESSAGE_ERROR,
                            gtk.BUTTONS_OK, msg);
                    result = dialog.run()
                    dialog.destroy()

            elif response == gtk.RESPONSE_CANCEL:
                pass
            dialog.destroy()

    def on_scroll_event(self,entry,event):
        if event.direction == gtk.gdk.SCROLL_UP: 
            delta = 1
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            delta = -1
        else:
            return
        if curr.load_from_pool(delta,self.wname):
            MainPanel.actualize_pool(self.wname,curr.charts[self.wname]) 

class ChartBrowser(gtk.VBox):
    def __init__(self,ap_path,font):
        gtk.VBox.__init__(self)
        self.chartview = None
        self.font = font
        appath = path.joinpath(ap_path,'astronex')
        
        liststore = gtk.ListStore(str)
        self.tables = gtk.ComboBoxEntry(liststore)
        self.entry = self.tables.get_children()[0]
        self.entry.set_editable(False)
        self.entry.connect('activate',self.on_search_activated)
        cell = gtk.CellRendererText()

        self.tables.pack_start(cell)
        self.tables.connect('changed',self.on_tables_changed)
        self.tables.set_size_request(120,-1)
        tablelist = curr.datab.get_databases()
        liststore.append([_('(Buscar)')]) 

        for c in tablelist:
            liststore.append([c])
        index = 0
        for i,r in enumerate(liststore):
            if r[0] == curr.database:
                index = i
                break 
        self.tables.set_active(index)
        
        hbox = gtk.HBox()
        hbox.pack_start(self.tables)
        
        opbut = gtk.Button()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"resources/folder-convert24.png")
        img.set_from_file(imgfile)
        opbut.set_image(img) 
        opbut.set_tooltip_text(_('Explorador/Tablas'))
        opbut.connect('clicked',self.on_opbut_clicked)
        hbox.pack_start(opbut,False,False) 

        opbut = gtk.Button()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"resources/pgram.png")
        img.set_from_file(imgfile)
        opbut.set_image(img) 
        opbut.set_tooltip_text(_('Planetograma'))
        opbut.connect('clicked',self.on_plagram_clicked)
        hbox.pack_start(opbut,False,False) 
        self.pack_start(hbox,False,False)
        
        self.chartmodel = gtk.ListStore(str,int)
        #self.chartview = gtk.TreeView(self.chartmodel)
        self.chartview = SearchView(self.chartmodel)
        selection = self.chartview.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        chartlist = curr.datab.get_chartlist(self.tables.get_active_text())

        for c in chartlist:
            glue = ", "
            if c[2] == '':  glue = ''
            self.chartmodel.append([c[2]+glue+c[1],int(c[0])])
        
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None,cell,text=0)
        self.chartview.append_column(column) 
        self.chartview.set_headers_visible(False)
        self.chartview.connect('row_activated',self.on_chart_activated)
        
        self.menu = gtk.Menu()
        for buf in (_('Copiar'),_('Cortar'),_('Pegar')):
            menu_items = gtk.MenuItem(buf)
            self.menu.append(menu_items)
            menu_items.connect("activate", self.on_menuitem_activate, buf)
            menu_items.show()
        self.chartview.connect('button_press_event',self.on_view_clicked)

        self.clip = None

        sw = gtk.ScrolledWindow()
        #sw.set_size_request(-1,160)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.chartview) 
        self.pack_start(sw,True,True)

    def on_opbut_clicked(self,but):
        boss.mainwin.launch_chartbrowser_from_mpanel() 
    
    def on_plagram_clicked(self,but):
        boss.mainwin.launch_plagram(None,None,None,None) 

    def relist(self,new):
        liststore = gtk.ListStore(str)
        tablelist = curr.datab.get_databases() 
        for c in tablelist:
            liststore.append([c])
        if not new:
            new = self.tables.get_active_text() 
        index = 0
        for i,r in enumerate(liststore):
            if r[0] == new:
                index = i
                break 
        self.tables.set_model(liststore)
        self.tables.set_active(index)

    def on_view_clicked(self,view,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 2:
            path = view.get_path_at_pos(int(event.x),int(event.y))[0]
            view.get_selection().select_path(path)
            model,iter = view.get_selection().get_selected()
            if not iter:
                return True
            id = model.get_value(iter,1)
            try:
                table = model.get_value(iter,2)
            except ValueError:
                table = self.tables.get_active_text()
            chart = curr.newchart()
            curr.datab.load_chart(table,id,chart)
            boss.mainwin.launch_aux_from_browser(chart)
            return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            x = int(event.x)
            y = int(event.y)
            pthinfo = view.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                view.grab_focus()
                view.set_cursor(path,col,0)
                if  self.clip is None:
                    self.menu.get_children()[2].set_sensitive(False)
                self.menu.popup(None, None, None, event.button, event.time)
            return True
        return False

    def on_menuitem_activate(self,menuitem,item): 
        model,iter = self.chartview.get_selection().get_selected()
        id = model.get_value(iter,1)
        table = self.tables.get_active_text()
        if item == _('Copiar') or item == _('Cortar'): 
            chart = curr.newchart()
            curr.datab.load_chart(table,id,chart)
            self.clip = chart
            menuitem.parent.get_children()[2].set_sensitive(True)
            if item == _('Cortar'):
                if not curr.safe_delete_chart(table,id):
                    msg = _('No puedo eliminar una carta con pareja!' )
                    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                            gtk.MESSAGE_WARNING,
                            gtk.BUTTONS_OK, msg);
                    result = dialog.run()
                    dialog.destroy()
                    return
                curr.datab.delete_chart(table,id)
                self.tables.emit('changed')
        else: # paste
            self.new_chart(self.clip)

    def on_search_activated(self,entry):
        if self.tables.get_active() > 0:
            return 
        searchlist = curr.datab.search_by_name_all_tables(entry.get_text())
        if not self.chartview is None:
            chartmodel = gtk.ListStore(str,int,str)
            for c in searchlist :
                glue = ", "
                if c[3] == '':  glue = ''
                chartmodel.append([c[3]+glue+c[2] , int(c[1]), c[0]])
            self.chartview.set_model(chartmodel)

    def on_tables_changed(self,combo): 
        if combo.get_active() == -1: return
        if combo.get_active() == 0: 
            self.entry.set_editable(True)
            self.entry.select_region(0,-1)
            self.entry.grab_focus()
            return
        else:
            if self.entry.get_editable():
                self.entry.set_editable(False)

        if not self.chartview is None:
            chartmodel = gtk.ListStore(str,int)
            chartlist = curr.datab.get_chartlist(self.tables.get_active_text()) 
            i = 0; r = 0
            for c in chartlist:
                glue = ", "
                if c[2] == '':  glue = ''
                chartmodel.append([c[2]+glue+c[1] , int(c[0]) ])
                if curr.curr_chart.first == c[1] and curr.curr_chart.last == c[2]:
                    r = i
                i += 1
            self.chartview.set_model(chartmodel)
            self.chartview.get_selection().select_path(r)
            self.chartview.scroll_to_cell(r)
            #self.chartview.row_activated(r,self.chartview.get_column(0))
    

    def on_chart_activated(self,view,path,col):
        model,iter = view.get_selection().get_selected()
        id = model.get_value(iter,1)
        try:
            table = model.get_value(iter,2)
        except ValueError:
            table = self.tables.get_active_text()
        chart = curr.charts[self.slot]
        curr.datab.load_chart(table,id,chart)
        curr.add_to_pool(copy(chart),Slot.overwrite)
        MainPanel.actualize_pool(self.slot,chart) 
        

    def constrainterror_dlg(self,fi,la):
        msg = _("Una carta con este nombre: %s %s existe. Sobrescribir?") % (fi,la)
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_OK_CANCEL, msg);
        result = dialog.run()
        dialog.destroy()
        return result
    
    def new_chart(self,chart):
        from sqlite3 import DatabaseError
        table = self.tables.get_active_text()
        try:
            lastrow = curr.datab.store_chart(table, chart) 
        except DatabaseError:
            result = self.constrainterror_dlg(chart.first,chart.last)
            if result != gtk.RESPONSE_OK:
                return None,None
            curr.datab.delete_chart_from_name(table,chart.first,chart.last)
            lastrow = curr.datab.store_chart(table, chart) 
            curr.fix_couples(table,chart.first,chart.last,lastrow)
        self.tables.emit('changed')
        return lastrow,table


class MainPanel(gtk.VBox):
    pool = {}
    active_slot = ''
    timeout_sid = None


    def __init__(self,manager):
        global curr, boss
        boss = manager
        gtk.VBox.__init__(self,False)
        
        appath = boss.app.appath
        curr = boss.get_state()
        
        frame = gtk.Frame()
        widget = Slot("master") 
        MainPanel.pool['master'] = widget
        frame.add(widget) 
        self.pack_start(frame,False)
        
        frame = gtk.Frame()
        widget = Slot("click") 
        MainPanel.pool['click'] = widget
        frame.add(widget) 
        self.pack_start(frame,False)
        
        frame = gtk.Frame()
        browser = ChartBrowser(appath,boss.opts.font)
        MainPanel.browser = browser
        frame.add(browser) 
        hbox = gtk.HBox()
        hbox.pack_start(frame,True,True)
        tb = self.make_toolbar(appath,boss)
        #frame = gtk.HandleBox()
        #frame.set_handle_position(gtk.POS_TOP)
        #frame.set_snap_edge(gtk.POS_TOP)
        #frame.set_size_request(-1,240)
        frame = gtk.Frame()
        frame.add(tb) 
        self.toolbar = tb
        hbox.pack_start(frame,False,False) 
        self.pack_start(hbox,True,True)
        
        self.chooser = OpPanel(boss)
        self.pack_end(self.chooser,True,True)

    def make_toolbar(self,appath,boss):
        appath = path.joinpath(appath,'astronex')
        tb = gtk.Toolbar()
        tb.set_orientation(gtk.ORIENTATION_VERTICAL)
        tb.set_size_request(-1,24)
        tb.set_tooltips(True)
        tb.set_style(gtk.TOOLBAR_ICONS)
        tb.set_show_arrow(True)

        tcal = gtk.ToggleToolButton()
        tcal.connect('clicked',self.on_calpanel,boss)
        img = gtk.Image()
        imgfile = path.joinpath(appath,"resources/cal.png")
        img.set_from_file(str(imgfile))
        tcal.set_icon_widget(img)
        tcal.set_tooltip_text(_("Calendario"))
        tb.insert(tcal,-1)
    
        tpe = gtk.ToggleToolButton()
        tpe.connect('clicked',self.on_pebut,boss)
        img = gtk.Image()
        imgfile = path.joinpath(appath,"resources/ap.png")
        img.set_from_file(str(imgfile))
        tpe.set_icon_widget(img)
        tpe.set_tooltip_text(_("Punto Edad"))
        tb.insert(tpe,-1)
    
        twin = gtk.ToolButton()
        twin.connect('clicked',self.on_auxwin,boss)
        img = gtk.Image()
        imgfile = path.joinpath(appath,"resources/new-win.png")
        img.set_from_file(str(imgfile))
        twin.set_icon_widget(img)
        twin.set_tooltip_text(_("Ventana auxiliar"))
        tb.insert(twin,-1)
    
        tasp = gtk.ToggleToolButton()
        tasp.connect('clicked',self.on_plsel,boss)
        img = gtk.Image()
        imgfile = path.joinpath(appath,"resources/aspects.png")
        img.set_from_file(str(imgfile))
        tasp.set_icon_widget(img)
        tasp.set_tooltip_text(_("Selector de aspectos"))
        tb.insert(tasp,-1)

        tcyc = gtk.ToggleToolButton()
        tcyc.connect('clicked',self.on_cycles,boss)
        img = gtk.Image()
        imgfile = path.joinpath(appath,"resources/cycles2.png")
        img.set_from_file(str(imgfile))
        tcyc.set_icon_widget(img)
        tcyc.set_tooltip_text(_("Selector de ciclos"))
        tb.insert(tcyc,-1)

        tdia = gtk.ToggleToolButton()
        tdia.connect('clicked',self.on_diada,boss)
        img = gtk.Image()
        imgfile = path.joinpath(appath,"resources/subdia.png")
        img.set_from_file(str(imgfile))
        tdia.set_icon_widget(img)
        tdia.set_tooltip_text(_("Diagramas"))
        tb.insert(tdia,-1)

        tdia = gtk.ToggleToolButton()
        tdia.connect('clicked',self.on_pebridge,boss)
        img = gtk.Image()
        imgfile = path.joinpath(appath,"resources/bridge.png")
        img.set_from_file(str(imgfile))
        tdia.set_icon_widget(img)
        tdia.set_tooltip_text(_("PE puente"))
        tb.insert(tdia,-1)

        #for but in tb:
        #    but.connect("create-menu-proxy",self.tb_proxy)

        return tb

    def tb_proxy(self,ti):
        pix = ti.get_icon_widget().get_pixbuf()
        img = gtk.Image()
        img.set_from_pixbuf(pix)
        mitem = gtk.ImageMenuItem()
        mitem.set_image(img)
        ti.set_proxy_menu_item(ti.__str__(),mitem)
        return True

    def on_calpanel(self,but,boss):
        if but.get_active():
            boss.da.show_panel()
        else:
            boss.da.hide_panel()

    def on_pebut(self,but,boss):
        if but.get_active():
            boss.da.show_pe()
        else:
            boss.da.hide_pe()

    def on_auxwin(self,but,boss):
        boss.da.make_auxwin()
    
    def on_plsel(self,but,boss):
        if but.get_active():
            boss.da.make_plsel()
        else:
            boss.da.plselector.exit()

    def on_cycles(self,but,boss):
        if but.get_active():
            boss.da.make_cycleswin() 
        else:
            boss.da.cycleselector.exit()

    def on_diada(self,but,boss):
        if but.get_active():
            boss.da.show_diada()
        else:
            boss.da.hide_diada()

    def on_pebridge(self,but,boss):
        if but.get_active():
            boss.da.make_pebridge() 
        else:
            boss.da.hide_pebridge()
    
    @classmethod
    def now_timeout(panel):
        curr.set_now()
        panel.act_now(curr.charts['now'])
        return True

    @classmethod
    def start_timeout(panel,tm=5):
        if not panel.timeout_sid:
            boss.da.panel.nowbut.emit('clicked')
            panel.timeout_sid = gobject.timeout_add(tm*1000,panel.now_timeout)
            
    @classmethod
    def stop_timeout(panel):
        if panel.timeout_sid:
            gobject.source_remove(panel.timeout_sid)
            panel.timeout_sid = None

    @staticmethod
    def update_slot_label(slot,chart):
        slot.chart_id = chart.id
        slot.namelbl.set_markup("<span foreground='blue'>"+chart.first+' '+chart.last+"</span>")
        strdate = chart.date
        date,time = parsestrtime(strdate)
        slot.loclbl.set_text(chart.city) 
        region = chart.region
        if boss.opts.lang == 'ca' and chart.country == u'España':
            region = cata_reg[region]
        slot.reglbl.set_text(t(chart.country)+' ('+region+')') 
        geo = format_longitud(chart.longitud) + ' '+ format_latitud(chart.latitud)
        slot.datelbl.set_text(date+' '+time+' '+geo)

    @classmethod
    def init_pools(panel):
        chart = curr.now 
        for slot in ['master','click']:
            panel.update_slot_label(panel.pool[slot],chart) 
        curr.curr_chart = curr.curr_click = chart 
        boss.da.redraw()
        widget = panel.pool['master']
        MainPanel.slot_activate(widget)
        widget.storage_but.emit("clicked")
        #panel.start_timeout()
        if curr.load_from_pool(0,'click'):
            panel.actualize_pool('click',curr.charts['click']) 

    @classmethod
    def act_now(panel,chart):
        master_slot = panel.pool['master'] 
        click_slot = panel.pool['click'] 
        if master_slot.chart_id != 'now' and click_slot.chart_id != 'now':
            #panel.stop_timeout()
            return

        slot = panel.pool[panel.active_slot]
        if slot.chart_id == 'now':
            panel.update_slot_label(slot,chart) 
            curr.curr_chart = chart
        other = panel.pool[slot.other]
        if other.chart_id == 'now':
            panel.update_slot_label(other,chart) 
            curr.curr_click = chart 

    @staticmethod
    def actualize_pool(slot,chart): 
        slot = MainPanel.pool[slot] 

        if boss.da.cycleselector and slot.wname == MainPanel.active_slot:
            cycles = chart.get_cycles()
            boss.da.cycleselector.adj.set_value(cycles+1) 
        
        if slot.wname == MainPanel.active_slot:
            curr.curr_chart = chart
        else:
            curr.curr_click = chart 
        MainPanel.update_slot_label(slot,chart) 

        if curr.curr_op == "sec_prog":
            boss.da.panel.nowbut.emit('clicked')

        boss.redraw()
        boss.da.redraw_auxwins()

    @staticmethod
    def slot_activate(slot):
        event = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
        event.button = 1
        event.time = 0
        slot.emit("button_press_event",event)

    @classmethod
    def slot_act_inactive(panel):
        slot = panel.pool[panel.active_slot]
        slot = panel.pool[slot.other]
        panel.slot_activate(slot)
        
    @classmethod
    def swap_storage(panel):
        slot = panel.pool[Slot.storage]
        slot = panel.pool[slot.other]
        slot.storage_but.emit('clicked')
    
    @classmethod
    def scroll_pool(panel,delta):
        slot = panel.active_slot
        if curr.load_from_pool(delta,slot):
            panel.actualize_pool(slot,curr.charts[slot]) 
