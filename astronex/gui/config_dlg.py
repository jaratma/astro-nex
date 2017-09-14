# -*- coding: utf-8 -*-
import os
import gtk,pango
from configobj import ConfigObj
from .. extensions.path import path
from localwidget import LocWidget 
from itertools import izip,count
from configobj import ConfigObj
from searchview import SearchView

from .. boss import boss
curr = boss.get_state()

MARKUP = "<b><i>%s</i></b>"
elem = ["fire","earth","air","water"]
plan = ["pers","trans","tool","node"]
asp = ["orange","red","blue","green"]
aux = ['click1','click2','inv','low','transcol']

class ConfigDlg(gtk.Dialog):
    '''Property dialog'''
    groups = [_("Localidad"), _("Tablas"), _("Colores"),
            _("Lineas"), _("Fuentes"), _("Orbes"),_("Lenguage"), _("PNG")]

    def __init__(self,parent):
        opts = boss.opts
        self.config_file = path.joinpath(boss.home_dir,boss.config_file)

        gtk.Dialog.__init__(self,
                _("Configuracion"), parent,
                gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CLOSE, gtk.RESPONSE_NONE,
                    gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        self.set_size_request(550,380)

        hbox = gtk.HBox()
        hbox.set_border_width(3)
        hbox.pack_start(self.index_table(),False,False)
        hbox.pack_start(gtk.VSeparator(),False,False)

        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(True)

        widget = ConfLocWidget()
        self.notebook.append_page(self.build_nbpage(widget,
            (_("Localidad por defecto"))))

        widget = TablesPage(boss.datab)
        self.notebook.append_page(self.build_nbpage(widget,
            (_("Tablas por defecto"))))

        widget = ColorsPage()
        self.notebook.append_page(self.build_nbpage(widget,
            (_("Colores"))))
        
        widget = LinesPage()
        self.notebook.append_page(self.build_nbpage(widget,
            (_("Lineas"))))
        
        widget = FontsPage()
        self.notebook.append_page(self.build_nbpage(widget,
            (_("Fuentes"))))
        
        widget = OrbsPage()
        self.notebook.append_page(self.build_nbpage(widget,
            (_("Orbes"))))
        
        widget = LangPage()
        self.notebook.append_page(self.build_nbpage(widget,
            (_("Lenguage por defecto"))))
        
        widget = PngPage()
        self.notebook.append_page(self.build_nbpage(widget,
            (_("Tamano de imagen PNG"))))
        
        hbox.pack_start(self.notebook,True,True) 
        self.vbox.pack_start(hbox,True,True)
        self.connect("response", self.dlg_response)
        self.show_all()

        wpos = self.window.get_position()
        self.pos_x = wpos[0]
        self.pos_y = wpos[1]

    def dlg_response(self,dialog,rid):
        if rid == gtk.RESPONSE_OK:
            conf = ConfigObj(self.config_file)
            boss.opts.opts_to_config(conf)
            conf.write()
        dialog.destroy()
        return
    
    def on_configure_event(self,widget,event):
        self.pos_x = event.x
        self.pos_y = event.y
    
    def index_table(self):
        model = gtk.ListStore(str)
        #view = gtk.TreeView(model)
        view = SearchView(model)
        view.set_size_request(100,-1)
        view.set_rules_hint(True)
        selection = view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        for o in self.groups:
            model.append((o,))
        cell = gtk.CellRendererText()
        cell.weight = 600
        column = gtk.TreeViewColumn(None,cell,text=0)
        view.append_column(column)
        view.set_headers_visible(False) 
        view.set_enable_search(False)
        sel = view.get_selection()
        sel.set_mode(gtk.SELECTION_SINGLE)
        sel.connect('changed',self.on_sel_changed)
        return view
    
    def on_sel_changed(self,sel):
        model, iter = sel.get_selected()
        index = model.get_path(iter)[0]
        self.notebook.set_current_page(index)
    
    def build_nbpage(self,widget,text):
        vbox = gtk.VBox()
        label = gtk.Label()
        label.set_markup(MARKUP % text)
        vbox.pack_start(label,False,False)
        vbox.pack_start(gtk.HSeparator(),False,False)
        vbox.pack_start(widget) 
        return vbox

class ConfLocWidget(LocWidget):
    def __init__(self): 
        LocWidget.__init__(self,default=True)
        self.country_combo.set_size_request(-1,-1)
        self.reg_combo.set_size_request(-1,-1)
        
    def on_row_activate(self,tree,path,col):
        return

    def actualize_if_needed(self,city,code):
        curr.setloc(city,code) 
        boss.opts.locality = city
        boss.opts.region = code
    
    def set_country_code(self,code):
        curr.country = code
        boss.opts.country = code

    def on_usa_toggled(self,check,cpl,lbl):
        LocWidget.on_usa_toggled(self,check,cpl,lbl)
        usa = ['false','true'][check.get_active()]
        boss.opts.usa = usa

class TablesPage(gtk.VBox):
    def __init__(self,datab):
        gtk.VBox.__init__(self)
        self.set_border_width(6)

        wtab = gtk.Table(3,2)
        wtab.set_row_spacings(6)
        wtab.set_col_spacings(6)
        wtab.set_homogeneous(False)
        label = gtk.Label(_('Inicio: ')) 
        liststore,index = self.get_table_list(datab,boss.opts.database)
        table = gtk.ComboBoxEntry(liststore)
        table.child.set_editable(False)
        cell = gtk.CellRendererText()
        table.pack_start(cell,False)
        table.connect('changed',self.on_tables_changed)
        table.set_active(index)
        hb = gtk.HBox(); hb.pack_end(label,False,False)
        wtab.attach(hb,0,1,0,1)
        wtab.attach(table,1,2,0,1)
        
        label = gtk.Label(_('Favoritos: ')) 
        liststore,index = self.get_table_list(datab,boss.opts.favourites)
        table = gtk.ComboBoxEntry(liststore)
        table.child.set_editable(False)
        cell = gtk.CellRendererText()
        table.pack_start(cell,False)
        table.connect('changed',self.on_fav_changed)
        if index > -1:
            table.set_active(index)
        
        hb = gtk.HBox(); hb.pack_end(label,False,False)
        wtab.attach(hb,0,1,1,2)
        wtab.attach(table,1,2,1,2)
        
        label = gtk.Label(_('N. favoritos: ')) 
        nfav = int(boss.opts.nfav)
        adj = gtk.Adjustment(nfav, 1, 10, 1, 1, 1)
        spin = gtk.SpinButton(adj)
        spin.set_alignment(1.0)
        spin.connect('value-changed', self.on_spin_changed)
        hb = gtk.HBox(); hb.pack_end(label,False,False)
        wtab.attach(hb,0,1,2,3)
        wtab.attach(spin,1,2,2,3,xpadding=60)
        
        align = gtk.Alignment(0.5,0.5)
        align.add(wtab)
        self.pack_start(align,False,False)

    def get_table_list(self,datab,default):
        liststore = gtk.ListStore(str)
        tablelist = datab.get_databases() 
        for c in tablelist:
            liststore.append([c])
        index = -1
        for i,r in enumerate(liststore):
            if r[0] == default:
                index = i
                break 
        return (liststore,index)
    
    def on_tables_changed(self,combo):
        boss.opts.database = combo.get_active_text()
    
    def on_fav_changed(self,combo):
        tbl = boss.opts.favourites = combo.get_active_text() 
        nfav = int(boss.opts.nfav)
        curr.fav = curr.datab.get_favlist(tbl,nfav,curr.newchart()) 

    def on_spin_changed(self,spin):
        value = spin.get_value_as_int()
        boss.opts.nfav = value
        tbl = boss.opts.favourites 
        curr.fav = curr.datab.get_favlist(tbl,value,curr.newchart()) 
    
class ColorsPage(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.set_border_width(6)
        cols = boss.get_colors()

        table = gtk.Table(6,4) 
        labels = [(_("Fuego"),'fire'),(_("Tierra"),'earth'),
                (_("Aire"),'air'),(_("Agua"),'water'),
                (_("Pers."),'pers'),(_("Herr."),'tool'),
                (_("Trans."),'trans'),(_("Nodo"),'node'),
                (_("Conj."),'orange'),(_("Rojo"),'red'),
                (_("Azul"),'blue'),(_("Verde"),'green')]
        
        self.make_table(table,labels,4,cols) 
        table.set_col_spacing(1,3)
        table.set_col_spacing(3,3)
        table.set_row_spacing(3,6)
        self.pack_start(table,False,False)

        table = gtk.Table(4,3) 
        labels = [(_("Primera pers."),'click1'),(_("Segunda pers."),'click2'),
                (_("P. Inversion"),'inv'),(_("P. Reposo"),'low')]
        self.make_table(table,labels,2,cols) 
            
        lbl = gtk.Label(_('Transitos'))
        lbl.set_alignment(0.0,0.5)
        colbut = gtk.ColorButton(gtk.gdk.color_parse(cols['transcol']))
        colbut.set_data('label','transcol')
        colbut.connect('color_set',self.color_set_cb, 'transcol')
        table.attach(lbl,0,1,3,4)
        table.attach(colbut,1,2,3,4)
        table.set_col_spacings(10)
        self.pack_start(table,False,False)

        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_END) 
        button = gtk.Button(_("Restablecer"))
        button.connect('clicked',self.color_reset)
        buttbox.pack_start(button,False,False)
        self.pack_end(buttbox,False,False)
    
    def make_table(self,table,labels,ix,cols):
        for i in range(len(labels)):
            lbl = gtk.Label(labels[i][0])
            lbl.set_alignment(0.0,0.5)
            colbut = gtk.ColorButton(gtk.gdk.color_parse(cols[labels[i][1]]))
            colbut.set_data('label',labels[i][1])
            colbut.connect('color_set',self.color_set_cb, labels[i][1])
            r = i % ix ; cc = (i / ix) * 2
            table.attach(lbl,cc,cc+1,r,r+1)
            table.attach(colbut,cc+1,cc+2,r,r+1)

    def color_set_cb(self,colbut,lbl):
        r = hex(colbut.get_color().red)[2:].rjust(4,'0')
        g = hex(colbut.get_color().green)[2:].rjust(4,'0')
        b = hex(colbut.get_color().blue)[2:].rjust(4,'0')
        cols = boss.get_colors()
        cols[lbl] ='#'+r+g+b
        setattr(boss.opts,lbl,r+g+b)
        if lbl in elem:
            boss.opts.zodiac.set_zodcolors()
        elif lbl in plan:
            boss.opts.zodiac.set_plancolors()
        elif lbl in asp:
            boss.opts.zodiac.set_aspcolors()
        elif lbl in aux:
            boss.opts.zodiac.set_auxcolors()
        boss.redraw()

    def color_reset(self,but):
        boss.reset_colors()
        boss.opts.zodiac.set_allcolors()
        boss.redraw()
        cols = boss.get_colors()
        for ch0 in self.get_children():
            for ch1 in ch0.get_children():
                if isinstance(ch1,gtk.ColorButton):
                    lbl = ch1.get_data('label')
                    ch1.set_color(gtk.gdk.color_parse(cols[lbl]))


class LinesPage(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.set_border_width(6)

        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_EDGE) 
        label = gtk.Label(_("Base"))
        buttbox.pack_start(label)
        base = float(boss.opts.base)
        adj = gtk.Adjustment(base, 0.2, 2.4, 0.05, 0.1, 0)
        spin = gtk.SpinButton(adj,0.0,2)
        spin.connect('value-changed', self.line_set_cb)
        buttbox.pack_start(spin)
        self.pack_start(buttbox,False)

    def line_set_cb(self, spin):
        value = spin.get_value()
        boss.opts.base = value
        boss.redraw()

class FontsPage(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.set_border_width(6)
        self.set_spacing(8)

        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_SPREAD) 
        fontbutton = gtk.FontButton(boss.opts.font)
        fontbutton.set_use_font(True)
        fontbutton.set_title(_("Elige una fuente"))
        fontbutton.connect('font-set', self.font_set_cb)
        buttbox.pack_start(fontbutton)
        self.pack_start(buttbox,False,True)
        
        font = pango.FontDescription("Astro-Nex")
        buttbox = gtk.HButtonBox() 
        buttbox.set_layout(gtk.BUTTONBOX_SPREAD) 
        store = gtk.ListStore(str)
        store.append([' z c '])
        store.append([' Z C '])
        combo = gtk.ComboBox(store)
        combo.set_border_width(3)
        cell = gtk.CellRendererText()
        cell.set_property('font-desc',font)
        cell.set_property('alignment',pango.ALIGN_RIGHT)
        combo.pack_start(cell,True)
        combo.add_attribute(cell,'text',0) 
        combo.add_attribute(cell,'text',0) 
        combo.connect('changed',self.style_set_cb)
        style = [0,1][boss.opts.transtyle == 'classic' ] 
        combo.set_active(style)
        buttbox.pack_start(combo,False,True) 
        self.pack_start(buttbox,False)
    
    def font_set_cb(self, fontbutton):
        font = fontbutton.get_font_name()
        boss.opts.font = font
        boss.redraw()

    def style_set_cb(self,combo):
        s = ['huber','classic'][combo.get_active()]
        if s != boss.opts.transtyle:
            boss.opts.transtyle = s
            boss.opts.zodiac.swap_plan_style()
            zodiac = boss.opts.zodiac.__class__
            boss.da.drawer.planetmanager.glyphs = zodiac.plan[:]
            boss.da.redraw()

class OrbsPage(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.set_border_width(6)

        hbox = gtk.HBox()
        vbox = gtk.VBox()
        vbox.set_border_width(4)
        vbox.set_size_request(54,-1)
        font = pango.FontDescription("Astro-Nex")
        labs = ['','d,f', 'h,j,l', 'k,g','z,x,c']
        for l in labs:
            lbl = gtk.Label(l)
            lbl.modify_font(font)
            vbox.pack_start(lbl,False,False,4)
        frame = gtk.Frame()
        frame.add(vbox)
        hbox.pack_start(frame,False,False)
        
        frame = gtk.Frame()
        table = gtk.Table(5,5)
        table.set_border_width(6)
        table.set_row_spacings(3)
        table.set_col_spacings(12) 
        frame.add(table)
        labs = ['2','36','4','5','17']
        for j,l in enumerate(labs):
            lbl = gtk.Label(l)
            lbl.modify_font(font)
            table.attach(lbl,j,j+1,0,1)
        cat = ['lum','normal','short','far']
        for i,c in enumerate(cat):
            for j,o in enumerate(getattr(boss.opts,c)):
                lbl = gtk.Label(o)
                table.attach(lbl,j,j+1,i+1,i+2)
        hbox.pack_start(frame,False,False)
        align = gtk.Alignment(0.5,0.5)
        align.add(hbox)
        self.pack_start(align,False,False)

class LangPage(gtk.VBox):
    def __init__(self):
        self.langs = ['es','en','de','ca']
        init_lang = self.langs.index(boss.opts.lang)
        gtk.VBox.__init__(self)
        self.set_border_width(6)

        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_SPREAD) 
        label = gtk.Label(_("Cambiar lenguage"))
        buttbox.pack_start(label)
        
        store = gtk.ListStore(str)
        store.append([_('espanol')])
        store.append([_('ingles')])
        store.append([_('aleman')])
        store.append([_('catalan')])
        combo = gtk.ComboBox(store)
        cell = gtk.CellRendererText()
        combo.pack_start(cell,True)
        combo.add_attribute(cell,'text',0)
        combo.set_size_request(100,28)
        combo.connect('changed',self.lang_set_cb)
        combo.set_active(init_lang)
        buttbox.pack_start(combo)
        self.pack_start(buttbox,False)
        hbox = gtk.HBox()
        align = gtk.Alignment(0.5,0.5)
        label = gtk.Label(_("Los cambios tendran lugar depues de reiniciar la aplicacion"))
        label.set_size_request(300,-1)
        label.set_justify(gtk.JUSTIFY_CENTER)
        label.set_line_wrap(True)
        align.add(label)
        hbox.pack_start(align,True,True)
        hbox.set_border_width(6)
        self.pack_start(hbox,False)

    def lang_set_cb(self,combo): 
        lang = self.langs[combo.get_active()]
        boss.opts.lang = lang
        #boss.app.langs[lang].install()

class PngPage(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.set_border_width(6)

        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_EDGE) 
        label = gtk.Label(_("Horizontal"))
        buttbox.pack_start(label)
        hdim = gtk.Entry()
        hdim.set_text(str(boss.opts.hsize))
        lbl = 'hsize'
        hdim.connect('changed', self.png_set_cb,lbl)
        buttbox.pack_start(hdim)
        self.pack_start(buttbox,False)

        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_EDGE) 
        label = gtk.Label(_("Vertical"))
        buttbox.pack_start(label)
        vdim = gtk.Entry()
        vdim.set_text(str(boss.opts.vsize))
        lbl = 'vsize'
        vdim.connect('changed', self.png_set_cb,lbl)
        buttbox.pack_start(vdim) 
        self.pack_start(buttbox,False)

        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_EDGE) 
        lcheck = gtk.CheckButton(_("Etiquetas"))
        buttbox.pack_start(lcheck)
        active = boss.opts.labels == 'true'
        lcheck.set_active(active)
        lcheck.connect('toggled', self.png_lbl_cb)
        self.pack_start(buttbox,False)
    
    def png_set_cb(self,entry,lbl):
        opt = getattr(boss.opts,lbl)
        try:
            opt = int(entry.get_text())            
            setattr(boss.opts,lbl,opt)
        except ValueError:
            entry.set_text(str(opt)) 

    def png_lbl_cb(self,but):
        opt = ['false','true'][but.get_active()]
        boss.opts.labels = opt

