# -*- coding: utf-8 -*-
import gtk
import sys,os,re
import pickle 
from .. extensions.path import path
from searchview import SearchView

curr = None
boss = None
regex = re.compile("[A-Za-z][_A-Za-z0-9]*$")

class MixerPanel(gtk.HBox):
    TARGETS = [
        ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
        ('text/plain', 0, 1),
        ('TEXT', 0, 2),
        ('STRING', 0, 3),
        ]
    
    def __init__(self,parent):
        global curr,boss
        boss = parent.boss
        curr = boss.get_state()
        gtk.HBox.__init__(self)
        self.views = {}
        self.menus = {}
        self.clip = None 
        self.changes = False

        hbox = gtk.HBox()
        selector = self.make_tables_selector()
        hbox.pack_start(selector,False,False)
        hbox.pack_start(gtk.VSeparator(),False,False)
        vbox = gtk.VBox() 
        vbox.set_border_width(6)
        button = gtk.RadioButton(None,_('Copiar'))
        button.set_data('action','copy')
        button.connect('toggled',self.on_action_toggled)
        vbox.pack_start(button,False,False)
        button = gtk.RadioButton(button,_('Mover'))
        button.set_data('action','move')
        button.connect('toggled',self.on_action_toggled)
        vbox.pack_start(button,False,False) 
        align = gtk.Alignment(0.5,0.5)
        align.add(vbox)
        hbox.pack_start(align,False,False)
        hbox.pack_start(gtk.VSeparator(),False,False)

        selector = self.make_tables_selector()
        hbox.pack_start(selector,False,False)

        frame = gtk.Frame()
        frame.add(hbox)
        frame.set_border_width(6)
        self.pack_start(frame,False,False)
        #frame = gtk.Frame()
        #frame.set_border_width(6)
        adminpanel = self.make_admin_panel()  
        #frame.add(adminpanel)
        #self.pack_start(frame,False,False)
        self.pack_start(adminpanel,False,False)

    def make_tables_selector(self): 
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
        
        but = gtk.Button()
        img = gtk.Image()
        appath = boss.app.appath
        imgfile = path.joinpath(appath,"astronex/resources/refresh-18.png")
        img.set_from_file(str(imgfile))
        but.set_image(img)
        but.connect('clicked',self.on_refresh_clicked,tables)
        hbox = gtk.HBox()
        hbox.pack_start(tables,False,False)
        hbox.pack_start(but,False,False) 
        vbox.pack_start(hbox,False,False)

        chartmodel = gtk.ListStore(str,int)
        #chartview = gtk.TreeView(chartmodel)
        chartview = SearchView(chartmodel)
        selection = chartview.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        chartlist = curr.datab.get_chartlist(tables.get_active_text())

        for c in chartlist:
            glue = ", "
            if c[2] == '':  glue = ''
            chartmodel.append([c[2]+glue+c[1],int(c[0])])
        
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None,cell,text=0)
        chartview.append_column(column) 
        chartview.set_headers_visible(False)
        sel = chartview.get_selection()
        sel.set_mode(gtk.SELECTION_SINGLE)
        #sel.connect('changed',self.on_sel_changed)
        sel.select_path(0,)
        
        menu = gtk.Menu()
        menu_item = gtk.MenuItem(_('Eliminar'))
        menu.append(menu_item)
        menu_item.set_data('op','delete')
        menu_item.connect("activate", self.on_menuitem_activate,chartview)
        menu_item.show()
        menu_item = gtk.MenuItem(_('Deshacer'))
        menu.append(menu_item)
        menu_item.set_data('op','undo')
        menu_item.connect("activate", self.on_menuitem_activate,chartview)
        menu_item.show()
        chartview.connect("button_press_event", self.on_view_clicked,menu)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(chartview) 
        vbox.pack_start(sw,True,True) 
        tables.connect('changed',self.on_tables_changed,chartview)
        vbox.set_size_request(210,-1)
        
        chartview.enable_model_drag_source( gtk.gdk.BUTTON1_MASK,
                                                self.TARGETS,
                                                gtk.gdk.ACTION_COPY)
        chartview.enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT)

        chartview.connect("drag_data_get", self.drag_data_get_data)
        chartview.connect("drag_data_received", self.drag_data_received_data)
        chartview.connect("row-activated", self.on_row_activated)
        self.views[chartview] = tables

        return vbox

    def on_action_toggled(self,but):
        action = but.get_data('action')
        action = [gtk.gdk.ACTION_COPY,gtk.gdk.ACTION_MOVE][action == 'move']
        for view in self.views:
            view.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,self.TARGETS,action)
            view.enable_model_drag_dest(self.TARGETS,action) 
    
    def on_row_activated(self,view,path,col):
        table = self.views[view].get_active_text()
        self.parent.set_current_page(0)
        combo = self.parent.get_nth_page(0).tables
        model = combo.get_model()
        iter = model.get_iter_root()
        index = 0
        while iter:
            if model.get_value(iter,0) == table:
                index = int(model.get_path(iter)[0])
                break
            iter = model.iter_next(iter)
        combo.set_active(index)
        m,i = view.get_selection().get_selected()
        first,last = m.get_value(i,0).split(',')
        self.parent.get_nth_page(0).findchart(first,last)

    def on_view_clicked(self,view, event,menu):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            x = int(event.x)
            y = int(event.y)
            pthinfo = view.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                view.grab_focus()
                view.set_cursor(path,col,0)
                if  self.clip is None:
                    menu.get_children()[1].set_sensitive(False)
                else:
                    menu.get_children()[1].set_sensitive(True)
                menu.popup(None, None, None, event.button, event.time)
            return True
    
    def on_menuitem_activate(self,menuitem,view): 
        op = menuitem.get_data('op')
        table = self.views[view]
        tablename = table.get_active_text()
        if op == 'delete':
            model,iter = view.get_selection().get_selected()
            id = model.get_value(iter,1)
            chart = curr.newchart()
            curr.datab.load_chart(tablename,id,chart)
            self.clip = chart
            if not self.safe_delete(tablename,id):
                return
            curr.datab.delete_chart(tablename,id)
            model.remove(iter)
        elif op == 'undo' and self.clip:
            rowid = self.new_chart(self.clip,tablename)
            if rowid: 
                model,iter = view.get_selection().get_selected()
                row = [", ".join([self.clip.last,self.clip.first]),rowid]
                path = model.get_path(iter)
                model.insert(int(path[0]),row)
                self.clip = None
        self.changes = True

    def on_refresh_clicked(self,but,combo):
        combo.emit('changed')

    def on_tables_changed(self,combo,chartview): 
        if combo.get_active() == -1: return
        if chartview:
            chartmodel = gtk.ListStore(str,int)
            chartlist = curr.datab.get_chartlist(combo.get_active_text()) 
            for c in chartlist:
                glue = ", "
                if not c[2]:  glue = ''
                chartmodel.append([c[2]+glue+c[1] , int(c[0]) ])
            chartview.set_model(chartmodel)
            chartview.get_selection().select_path(0,)
            self.views[chartview] = combo
    
    def drag_data_get_data(self,treeview,context,selection,target_id,etime):
        treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected() 
        data = ";".join([model.get_value(iter, 0),str(model.get_value(iter, 1))])
        selection.set(selection.target, 8, data)

    def drag_data_received_data(self,treeview,context,x,y,selection,info,etime):
        for key in self.views.keys():
            if key == treeview:
                mytab = self.views[key].get_active_text()
            else:
                othertab = self.views[key].get_active_text()
        if mytab == othertab:
            return
        model = treeview.get_model()
        data = selection.data.split(";")
        srcid = int(data[-1])
        
        chart = curr.newchart()
        curr.datab.load_chart(othertab,srcid,chart)
        id = self.new_chart(chart,mytab)
        if not id:
            return
        data[-1] = id
        
        drop_info = treeview.get_dest_row_at_pos(x, y)
        if drop_info:
            path, position = drop_info
            iter = model.get_iter(path)
            if (position == gtk.TREE_VIEW_DROP_BEFORE
                or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                model.insert_before(iter, data)
            else:
                model.insert_after(iter, data)
        else:
            model.append(data)

        for key in self.views.keys():
            if key == treeview:
                mytab = self.views[key].get_active_text()
            else:
                othertab = self.views[key].get_active_text()
        self.changes = True
        if context.action == gtk.gdk.ACTION_MOVE:
            context.finish(True, True, etime)
            if not self.safe_delete(othertab,srcid):
                return
            curr.datab.delete_chart(othertab,srcid)
        return

    def constrainterror_dlg(self,fi,la):
        msg = _("Una carta con este nombre: %s %s existe. Sobrescribir?") % (fi,la)
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_OK_CANCEL, msg);
        result = dialog.run()
        dialog.destroy()
        return result
    
    def new_chart(self,chart,table):
        from sqlite3 import DatabaseError
        try:
            lastrow = curr.datab.store_chart(table, chart) 
        except DatabaseError:
            result = self.constrainterror_dlg(chart.first,chart.last)
            if result != gtk.RESPONSE_OK:
                return None
            curr.datab.delete_chart_from_name(table,chart.first,chart.last)
            lastrow = curr.datab.store_chart(table, chart) 
            curr.fix_couples(table,chart.first,chart.last,lastrow)
        return lastrow
    
    def clear_selected(self, button):
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)
        return

    def make_admin_panel(self):
        appath = boss.app.appath
        thebox = gtk.VBox()
        vbox = gtk.VButtonBox()
        vbox.set_layout(gtk.BUTTONBOX_SPREAD)
        vbox.set_border_width(3)
        
        #hbox = gtk.HBox()
        #but = gtk.Button(_('Compactar'))
        #but.connect('clicked',self.on_compact)
        #hbox.pack_start(but)
        #vbox.pack_start(hbox,False,False)

        hbox = gtk.HBox()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"astronex/resources/gtk-new-18.png")
        img.set_from_file(imgfile)
        hbox.pack_start(img)
        but = gtk.Button(_('_Crear tabla'))
        but.connect('clicked',self.on_create_table)
        hbox.pack_start(but)
        vbox.pack_start(hbox,False,False)
        
        hbox = gtk.HBox()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"astronex/resources/stock_delete.png")
        img.set_from_file(imgfile)
        hbox.pack_start(img)
        but = gtk.Button(_('E_liminar tabla'))
        but.connect('clicked',self.on_delete_table)
        hbox.pack_start(but)
        vbox.pack_start(hbox,False,False)
        
        hbox = gtk.HBox()
        img = gtk.Image()
        imgfile = path.joinpath(appath,"astronex/resources/gtk-convert-18.png")
        img.set_from_file(imgfile)
        hbox.pack_start(img)
        but = gtk.Button(_('_Renombrar'))
        but.connect('clicked',self.on_rename_table)
        hbox.pack_start(but)
        vbox.pack_start(hbox,False,False)
        
        frame = gtk.Frame()
        frame.set_border_width(6)
        frame.add(vbox)
        thebox.pack_start(frame)
        
        vbox = gtk.VButtonBox()
        vbox.set_layout(gtk.BUTTONBOX_SPREAD)
        vbox.set_border_width(3)
        
        hbox = gtk.HBox()
        but = gtk.Button(_('_Exportar  tabla'))
        but.connect('clicked',self.on_table_export)
        hbox.pack_start(but)
        vbox.pack_start(hbox,False,False)
        
        hbox = gtk.HBox()
        but = gtk.Button(_('_Importar  tabla'))
        but.connect('clicked',self.on_table_import)
        hbox.pack_start(but)
        vbox.pack_start(hbox,False,False)
        
        frame = gtk.Frame()
        frame.set_border_width(6)
        frame.add(vbox)

        thebox.pack_start(frame)
        return thebox

    def check_name(self,name):
        ok = regex.match(name)
        if not ok: 
            msg = [_("El nombre de las tablas solo puede comenzar con"),
                    _("'_' o letra*, seguida de letra*, numero o '_'."),
                    _("* A-Z, a-z, sin tildes ni caracteres compuestos") ]
            self.messagedialog("\n".join(msg))
        return ok

    def on_create_table(self,but):
        entry = gtk.Entry()
        dialog = gtk.Dialog(_("Nombre:"), None,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_NONE,
                    gtk.STOCK_OK, gtk.RESPONSE_OK))
        dialog.vbox.pack_end(entry, True, True)
        entry.grab_focus()
        dialog.connect("response", self.create_response)
        dialog.show_all()
    
    def create_response(self,dialog,rid):
        if rid == gtk.RESPONSE_NONE or rid == gtk.RESPONSE_DELETE_EVENT:
            dialog.destroy()
            return
        tablelist = curr.datab.get_databases() 
        new = dialog.vbox.get_children()[0].get_text()
        if not self.check_name(new):
            return 
        if new in tablelist:
            result = self.replacedialog(new)
            if result != gtk.RESPONSE_OK:
                return 
        #if not self.safe_delete_table(new):
        #    return
        curr.datab.create_table(new)
        self.relist(new)
        dialog.destroy()
    
    def replacedialog(self,tbl):
        msg = _("La tabla %s existe. Reemplazarla, perdiendo los datos?") % tbl
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_OK_CANCEL, msg);
        result = dialog.run()
        dialog.destroy()
        return result
    
    def relist(self,new):
        liststore = gtk.ListStore(str)
        tablelist = curr.datab.get_databases() 
        for c in tablelist:
            liststore.append([c])
        index = 0
        for i,r in enumerate(liststore):
            if r[0] == new:
                index = i
                break 
        for key in self.views.keys():
            table = self.views[key]
            table.set_model(liststore)
        table.set_active(index)
        self.changes = True

    def on_delete_table(self,but): 
        dialog = gtk.Dialog(_("Eliminar tabla"), None,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_NONE,
                    gtk.STOCK_OK, gtk.RESPONSE_OK))
        liststore = gtk.ListStore(str)
        tables = gtk.ComboBoxEntry(liststore)
        tables.set_size_request(250,-1)
        tables.get_children()[0].set_editable(False)
        cell = gtk.CellRendererText()
        tables.pack_start(cell)
        tablelist = curr.datab.get_databases() 
        for c in tablelist:
            liststore.append([c])
        tables.set_active(0) 
        dialog.vbox.pack_start(tables, True, True)
        dialog.connect("response", self.delete_response)
        dialog.show_all()

    def delete_response(self,dialog,rid):
        if rid == gtk.RESPONSE_NONE or rid == gtk.RESPONSE_DELETE_EVENT:
            dialog.destroy()
            return
        combo = dialog.vbox.get_children()[0]
        tbl = combo.get_active_text()
        if tbl == boss.opts.database or tbl == boss.opts.favourites:
            self.messagedialog(_("No puedo eliminar una tabla predeterminada."))
            return
        if not self.safe_delete_table(tbl):
            return
        result = self.deletedialog(tbl)
        if result == gtk.RESPONSE_OK:
            curr.datab.delete_table(tbl)
            self.relist('')
            dialog.destroy()

    def messagedialog(self,msg):
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                gtk.MESSAGE_INFO,
                gtk.BUTTONS_OK, msg);
        result = dialog.run()
        dialog.destroy()
    
    def deletedialog(self,tbl):
        msg = _("Desea realmente eliminar la tabla %s?") % tbl
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_OK_CANCEL, msg);
        result = dialog.run()
        dialog.destroy()
        return result

    def on_rename_table(self,but): 
        dialog = gtk.Dialog(_("Cambiar nombre"), None,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_NONE,
                    gtk.STOCK_OK, gtk.RESPONSE_OK))
        liststore = gtk.ListStore(str)
        tables = gtk.ComboBoxEntry(liststore)
        tables.set_size_request(250,-1)
        tables.get_children()[0].set_editable(False)
        cell = gtk.CellRendererText()
        tables.pack_start(cell)
        tablelist = curr.datab.get_databases() 
        for c in tablelist:
            liststore.append([c])
        tables.set_active(0) 
        dialog.vbox.pack_start(tables, True, True)
        entry = gtk.Entry()
        entry.set_text(tables.get_active_text())
        dialog.vbox.pack_start(entry, True, True)
        tables.connect('changed',self.on_renamecombo_changed,entry)        
        dialog.connect("response", self.rename_response)
        dialog.show_all()

    def on_renamecombo_changed(self,combo,entry):
        entry.set_text(combo.get_active_text()) 

    def rename_response(self,dialog,rid): 
        if rid == gtk.RESPONSE_NONE or rid == gtk.RESPONSE_DELETE_EVENT:
            dialog.destroy()
            return
        oldname = dialog.vbox.get_children()[0].get_active_text()
        newname = dialog.vbox.get_children()[1].get_text()
        if oldname == boss.opts.database or oldname == boss.opts.favourites:
            self.messagedialog(_("No puedo cambiar el nombre a una tabla predeterminada."))
            return
        if not self.safe_delete_table(oldname):
            return
        if not self.check_name(newname):
            return 
        curr.datab.rename_chart(oldname,newname)
        self.relist(newname)
        dialog.destroy()

    def on_table_export(self,but):
        dialog = gtk.Dialog(_("Exportar tabla"), None,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_NONE,
                    gtk.STOCK_OK, gtk.RESPONSE_OK))
        liststore = gtk.ListStore(str)
        tables = gtk.ComboBoxEntry(liststore)
        tables.set_size_request(250,-1)
        tables.get_children()[0].set_editable(False)
        cell = gtk.CellRendererText()
        tables.pack_start(cell)
        tablelist = curr.datab.get_databases() 
        for c in tablelist:
            liststore.append([c])
        tables.set_active(0) 
        dialog.vbox.pack_start(tables, True, True)
        dialog.connect("response", self.export_response)
        dialog.show_all()

    def export_response(self,dialog,rid):
        if rid == gtk.RESPONSE_NONE or rid == gtk.RESPONSE_DELETE_EVENT:
            dialog.destroy()
            return
        table = dialog.vbox.get_children()[0].get_active_text()

        if sys.platform == 'win32':
            import winshell
            folder = winshell.my_documents() + os.path.sep 
        else: 
            folder = os.path.expanduser("~") + os.path.sep
        name = folder + table + ".nxt"
        export = []
        
        chartlist = curr.datab.get_chartlist(table) 
        for c in chartlist:
            id = int(c[0])
            chart = curr.newchart()
            curr.datab.load_chart(table,id,chart)
            export.append(chart)
        
        output = open(name, 'wb')
        pickle.dump(export,output,-1)
        output.close()
        dialog.destroy()

    def on_table_import(self,but): 
        dialog = gtk.Dialog(_("Importar tabla"), None,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_NONE,
                    gtk.STOCK_OK, gtk.RESPONSE_OK))
        
        table = gtk.Table(2,3,False)
        table.set_col_spacings(3)
        lbl = gtk.Label(_('Archivo'))
        table.attach(lbl,0,1,0,1)
        entry = gtk.Entry()
        table.attach(entry,1,2,0,1)
        but = gtk.Button(_('Examinar'))
        table.attach(but,2,3,0,1)
        tname = gtk.Label(_('Tabla'))
        table.attach(tname,0,1,1,2)
        tentry = gtk.Entry()
        table.attach(tentry,1,2,1,2)
        info = gtk.Label()
        table.attach(info,2,3,1,2)
        dialog.vbox.pack_start(table,False,False)
        but.connect('clicked',self.on_filebrowse,entry,tentry)

        dialog.connect("response", self.import_response,entry,tentry,info)
        dialog.show_all()
        
    def import_response(self,dialog,rid,entry,tentry,info):
        if rid == gtk.RESPONSE_NONE or rid == gtk.RESPONSE_DELETE_EVENT:
            dialog.destroy()
            return 
        elif rid == gtk.RESPONSE_OK:
            name = tentry.get_text()
            if not self.check_name(name):
                return 
            tablelist = curr.datab.get_databases() 
            if name in tablelist:
                result = self.replacedialog(name)
                if result != gtk.RESPONSE_OK:
                    return 
            filename = entry.get_text()
            try:
                input = open(filename,'rb')
                imported = pickle.load(input)
            except IOError:
                self.messagedialog(_('Error abriendo el archivo'))
                return 
            except:
                self.messagedialog(_('Error importando la tabla'))
                return 
            curr.datab.create_table(name) 
            li = len(imported) 
            info.set_text('(%s)' % (li))
            for i,data in enumerate(imported):
                self.new_chart(data,name) 
                info.set_text(_('%s de %s') % (i,li))
                while (gtk.events_pending()):
                    gtk.main_iteration()
            self.relist('') 
            dialog.destroy()
            return

    def on_filebrowse(self,but,entry,tentry):
        dialog = gtk.FileChooserDialog("Abrir archivo...",
                                    None,
                                    gtk.FILE_CHOOSER_ACTION_OPEN,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        if sys.platform == 'win32':
            import winshell
            dialog.set_current_folder(winshell.my_documents())
        else: 
            dialog.set_current_folder(os.path.expanduser("~"))

        filename = None
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            entry.set_text(filename) 
            name = os.path.basename(os.path.splitext(filename)[0])
            tentry.set_text(name) 
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        return

    def on_compact(self,but):
        curr.datab.vacuum()

    def safe_delete(self,table,id): 
        if not curr.safe_delete_chart(table,id):
            msg = _('No puedo eliminar una carta con pareja!' )
            dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                    gtk.MESSAGE_WARNING,
                    gtk.BUTTONS_OK, msg);
            result = dialog.run()
            dialog.destroy()
            return False
        return True

    def safe_delete_table(self,table):
        if not curr.safe_delete_table(table):
            msg = _('No puedo eliminar una tabla con pareja!' )
            dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                    gtk.MESSAGE_WARNING,
                    gtk.BUTTONS_OK, msg);
            result = dialog.run()
            dialog.destroy()
            return False
        return True
