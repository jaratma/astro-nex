# -*- coding: utf-8 -*-
import gtk
import cairo, pango
from copy import copy
from .. drawing.coredraw import CoreMixin
from .. drawing.dispatcher import DrawMixin, AspectManager
from .. drawing.roundedcharts import RadixChart 
from mainnb import Slot
from .. utils import parsestrtime
from mixer import MixerPanel
from import_dlg import ImportPanel
from couples import CouplesPanel
from .. extensions.path import path
from searchview import SearchView

boss = None
curr = None
chart =  None
MainPanel = None

class ChartBrowserWindow(gtk.Window):
    def __init__(self,parent):
        global boss, curr, chart, MainPanel
        boss = parent.boss
        curr = parent.boss.get_state()
        chart = curr.newchart()
        MainPanel = parent.mpanel.__class__
        gtk.Window.__init__(self)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_transient_for(parent)
        #self.set_modal(True)
        self.set_destroy_with_parent(True)
        self.set_title(_("Explorador"))
        self.connect('destroy', self.cb_exit,parent)
        self.connect('focus-out-event', self.on_state)
        self.connect('configure-event', self.on_configure_event) 

        accel_group = gtk.AccelGroup()
        accel_group.connect_group(gtk.keysyms.Escape,0,gtk.ACCEL_LOCKED,self.escape)
        self.add_accel_group(accel_group) 
        
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_LEFT)
        notebook.connect('switch-page',self.page_select)

        label = gtk.Label(_("Explorador"))
        label.set_angle(90)
        notebook.append_page(BrowserPanel(parent),label)
        
        label = gtk.Label(_("Mezclador"))
        label.set_angle(90)
        notebook.append_page(MixerPanel(parent),label)

        label = gtk.Label(_("Importacion AAF"))
        label.set_angle(90)
        notebook.append_page(ImportPanel(parent),label)

        label = gtk.Label(_("Parejas"))
        label.set_angle(90)
        notebook.append_page(CouplesPanel(parent),label)
        
        self.add(notebook)
        self.set_default_size(650,400)
        self.show_all()
        wpos = self.window.get_position()
        self.pos_x = wpos[0]
        self.pos_y = wpos[1]

    def on_configure_event(self,widget,event):
        self.pos_x = event.x
        self.pos_y = event.y

    def page_select(self,nb,page,pnum): 
        page = nb.get_nth_page(pnum)
        try:
            if pnum == 0 and nb.get_nth_page(1).changes:
                page.relist()
        except AttributeError:
            pass 
        if page.__class__ == CouplesPanel:
            page.save_couples()
        title = nb.get_tab_label(page).get_text()
        self.set_title(title)

    def escape(self,a,b,c,d):
        self.destroy() 

    def on_state(self,e,event):
        if self.child.get_nth_page(1).changes:
            boss.mpanel.browser.tables.emit('changed')
            boss.mpanel.browser.relist('')

    def cb_exit(self,e,parent):
        parent.browser = None
        if self.child.get_nth_page(1).changes:
            boss.mpanel.browser.tables.emit('changed')
            boss.mpanel.browser.relist('')
        self.child.get_nth_page(3).save_couples()
        return False


class  BrowserPanel(gtk.HBox): 
    def __init__(self,parent):
        gtk.HBox.__init__(self)

        self.chartview = None
        hbox = gtk.HBox()

        vbox = gtk.VBox()        
        # tables
        liststore = gtk.ListStore(str)
        self.tables = gtk.ComboBoxEntry(liststore)
        self.tables.set_size_request(228,-1)
        self.tables.get_children()[0].set_editable(False)
        cell = gtk.CellRendererText()

        self.tables.pack_start(cell)
        self.tables.connect('changed',self.on_tables_changed)
        tablelist = curr.datab.get_databases()
        
        for c in tablelist:
            liststore.append([c])
        index = 0
        for i,r in enumerate(liststore):
            if r[0] == curr.database:
                index = i
                break 
        self.tables.set_active(index) 

        but = gtk.Button()
        img = gtk.Image()
        appath = boss.app.appath
        imgfile = path.joinpath(appath,"astronex/resources/refresh-18.png")
        img.set_from_file(str(imgfile))
        but.set_image(img)
        but.connect('clicked',self.on_refresh_clicked,self.tables)
        hhbox = gtk.HBox()
        hhbox.pack_start(self.tables,False,False)
        hhbox.pack_start(but,False,False) 
        vbox.pack_start(hhbox,False,False)
        
        #vbox.pack_start(self.tables,False,False)
        
        # chart list
        self.chartmodel = gtk.ListStore(str,int)
        #self.chartview = gtk.TreeView(self.chartmodel)
        self.chartview = SearchView(self.chartmodel)
        selection = self.chartview.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        chartlist = curr.datab.get_chartlist(self.tables.get_active_text())

        for c in chartlist:
            glue = ", "
            if c[2] == '':  glue = ''
            self.chartmodel.append([c[2]+glue+c[1] , int(c[0]) ])
        
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None,cell,text=0)
        self.chartview.append_column(column) 
        self.chartview.set_headers_visible(False)
        self.chartview.connect('row_activated',self.on_chart_activated)
        sel = self.chartview.get_selection()
        sel.set_mode(gtk.SELECTION_SINGLE)
        sel.connect('changed',self.on_sel_changed)
        sel.select_path(0,)
        self.chartview.grab_focus()
        
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.chartview) 
        vbox.pack_start(sw,True,True)
        
        # drawer
        hbox.pack_start(vbox,False,False)
        hbox.pack_start(gtk.VSeparator(),False,False)
        self.chsnap = ChartSnapshot(parent.boss)
        self.chsnap.set_size_request(400,400) 
        hbox.pack_start(self.chsnap)
        frame = gtk.Frame()
        frame.set_border_width(6)
        frame.add(hbox)
        self.add(frame)

    def on_refresh_clicked(self,but,combo):
        combo.emit('changed')
    
    def findchart(self,first,last):
        model = self.chartview.get_model()
        iter = model.get_iter_root()
        while iter:
            tfirst,__,tlast = model.get_value(iter,0).partition(',')
            if first == tfirst and last == tlast:
                self.chartview.get_selection().select_path(model.get_path(iter)) 
                break
            iter = model.iter_next(iter)

    def on_tables_changed(self,combo): 
        if combo.get_active() == -1: return
        if not self.chartview is None:
            chartmodel = gtk.ListStore(str,int)
            chartlist = curr.datab.get_chartlist(self.tables.get_active_text()) 
            for c in chartlist:
                glue = ", "
                if c[2] == '':  glue = ''
                chartmodel.append([c[2]+glue+c[1] , int(c[0]) ])
            self.chartview.set_model(chartmodel)
            self.chartview.get_selection().select_path(0,)
    
    def on_sel_changed(self,sel):
        model, iter = sel.get_selected()
        if not iter:
            sel.select_path(0,)
            model, iter = sel.get_selected()
        id = model.get_value(iter,1)
        table = self.tables.get_active_text()
        curr.datab.load_chart(table,id,chart)
        try:
            self.chsnap.redraw()
        except AttributeError:
            pass

    def on_chart_activated(self,view,path,col):
        model,iter = view.get_selection().get_selected()
        id = model.get_value(iter,1)
        chart = curr.charts[Slot.storage]
        table = self.tables.get_active_text()
        curr.datab.load_chart(table,id,chart)
        curr.add_to_pool(copy(chart),Slot.overwrite)
        MainPanel.actualize_pool(Slot.storage,chart) 

    def relist(self):
        liststore = gtk.ListStore(str)
        tablelist = curr.datab.get_databases() 
        for c in tablelist:
            liststore.append([c])
        self.tables.set_model(liststore)


class ChartSnapshot(gtk.DrawingArea):
    def __init__(self,boss):
        self.boss = boss
        self.opts = boss.opts
        gtk.DrawingArea.__init__(self)
        self.connect("expose_event",self.dispatch)
        self.drawer = SnapMixin(boss.opts,self) 

    def dispatch(self,da,event):
        cr = self.window.cairo_create()
        w = self.allocation.width
        h = self.allocation.height
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgb(1.0,1.0,0.95)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(self.opts.base))
        
        chartobject = RadixChart(chart, None)
        self.drawer.draw_nat(cr,w,h,chartobject)
        self.d_label(cr,w,h,chart)
        return True

    def redraw(self): 
        w = self.allocation.width
        h = self.allocation.height
        self.window.invalidate_rect(gtk.gdk.Rectangle(0,0,w,h),False)

    def d_label(self,cr,w,h,chart):
        cr.identity_matrix()
        font = pango.FontDescription(self.opts.font)
        font.set_size(7*pango.SCALE)
        layout = cr.create_layout()
        layout.set_font_description(font)
        date,time = parsestrtime(chart.date)
        date = date + " - " + time.split(" ")[0]
        name = chart.first + " " + chart.last
        layout.set_text('%s  (%s)' % (name,date))
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.set_source_rgb(0.0,0,0.5)
        cr.move_to(w-xpos-5,h-12)
        cr.show_layout(layout)

R_ASP = 0.435
class SnapMixin(CoreMixin):
    def __init__(self,opts,surface):
        self.opts = opts
        self.surface = surface
        self.aspmanager = AspectManager(boss,self.get_gw,self.get_uni,self.get_nw, DrawMixin.planetmanager,opts.zodiac.aspcolors,opts.base)
        CoreMixin.__init__(self,opts.zodiac,surface)
    
    def draw_nat(self,cr,width,height,chartob):
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        cr.translate(cx,cy)

        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT')
        self.draw_cusps(cr,radius,chartob)
        self.d_year_lines(cr,radius,chartob)
        self.d_golden_points(cr,radius,chartob)
        self.d_cross_points(cr,radius,chartob)
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)

    def get_gw(self):
        return False

    def get_uni(self):
        return True

    def get_nw(self,f=None):
        return []
