# -*- coding: utf-8 -*-
import gtk
import cairo, pango
from copy import copy
from math import pi as PI
from .. drawing.coredraw import CoreMixin
from .. drawing.biograph import BioMixin
from .. drawing.dispatcher import DrawMixin, AspectManager
from .. drawing.roundedcharts import Basic_Chart,RadixChart,NodalChart
from mainnb import Slot

curr = None
boss = None
chart =  None
get_AP_DEG = None

class BridgePEWindow(gtk.Window):
    def __init__(self,parent):
        global boss, curr, chart, get_AP_DEG
        curr = parent.boss.get_state()
        boss = parent.boss
        self.parnt = parent
        get_AP_DEG = parent.boss.da.drawer.get_AP_DEG
        gtk.Window.__init__(self)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_title(_("PE Puente"))
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK) 
        self.connect('destroy', self.cb_exit,parent) 
        self.connect('button-press-event', self.clicked)

        accel_group = gtk.AccelGroup()
        accel_group.connect_group(gtk.keysyms.Escape,0,gtk.ACCEL_LOCKED,self.escape)
        self.add_accel_group(accel_group) 
        
        # drawer
        bridge = BridgeArea(parent.boss)
        bridge.set_size_request(450,450) 
        frame = gtk.Frame()
        frame.add(bridge)
        self.add(frame)
        self.sda = bridge
        self.set_decorated(False) 
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height()
        self.move(width-450,height-450)
        self.show_all()
    
    def exit(self):
        self.destroy()
    
    def escape(self,a,b,c,d):
        self.destroy() 

    def cb_exit(self,e,parent):
        parent.boss.mpanel.toolbar.get_nth_item(6).set_active(False) 
        return False
    
    def clicked(self,w,event):
        w.set_decorated(not w.get_decorated())

alts = ['nat','nod']

class BridgeArea(gtk.DrawingArea):
    pepending = [False,None,None]

    def __init__(self,boss):
        self.boss = boss
        self.opts = boss.opts
        gtk.DrawingArea.__init__(self)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | 
                gtk.gdk.BUTTON_RELEASE_MASK | 
                gtk.gdk.POINTER_MOTION_MASK | 
                gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.connect("expose_event",self.dispatch)
        self.connect("scroll-event", self.on_scroll)        
        self.drawer = Drawer(boss.opts,self) 
        self.ops = ['draw','bio']

    def dispatch(self,da,event):
        self.drawer.pe_zones = self.boss.da.drawer.pe_zones
        cr = self.window.cairo_create()
        w = self.allocation.width
        h = self.allocation.height
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgb(0.98,1.0,0.98)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(self.opts.base))
        
        chart_one, chart_two = curr.curr_chart, curr.curr_click
        if curr.opmode != 'simple':
            currop = curr.opleft
        else:
            currop = curr.curr_op
        op,alt = currop.split('_')
        currop = '_'.join([self.ops[0],alts[alt == 'nat']])
        chartobject = Basic_Chart(chart_one, chart_two)
        getattr(self.drawer,currop)(cr,w,h,chartobject)
        
        cr.identity_matrix()
        self.draw_pelabel(cr,w,h)
        self.draw_label(cr,w,h)

    def on_scroll(self,da,event):
        self.ops[0],self.ops[1] = self.ops[1],self.ops[0]
        self.redraw()
        return True 

    def redraw(self): 
        w = self.allocation.width
        h = self.allocation.height
        self.window.invalidate_rect(gtk.gdk.Rectangle(0,0,w,h),False)

    def draw_pelabel(self,cr,w,h):
        date = self.dt
        date = date.__str__().split(' ')[0].split('-')
        date.reverse()
        date = "/".join(date) 
        layout = cr.create_layout()
        cr.set_source_rgb(0,0,0.6) 
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        layout.set_text(date)
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to(w-xpos-5,5)
        cr.show_layout(layout)

    def draw_label(self,cr,w,h): 
        chart = curr.curr_chart
        name = "%s %s" % (chart.first,chart.last) 
        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        col = (0,0,0.4) 
        layout.set_text(name)
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.set_source_rgb(*col) 
        cr.move_to(w-xpos-5,h-15)
        cr.show_layout(layout)

R_ASP = 0.435
MAGICK_FONTSCALE = 0.0012
ruler = [0.9,0.5]

class Drawer(CoreMixin,BioMixin):
    asplet = ( '1','2','3','4','5','6','7','6','5','4','3','2' )
    
    def __init__(self,opts,surface):
        self.opts = opts
        self.surface = surface
        self.aspmanager = AspectManager(boss,self.get_gw,self.get_uni,self.get_nw, DrawMixin.planetmanager,opts.zodiac.aspcolors,opts.base)
        CoreMixin.__init__(self,opts.zodiac,surface)
        BioMixin.__init__(self,opts.zodiac)
        self.rightdraw = False
        self.pe_zones = False
    
    def make_crown(self,cr,radius,chartob):
        if self.pe_zones:
            self.d_pe_zones(cr,radius,chartob)
        self.d_radial_lines(cr,radius,chartob)
        self.make_all_rulers(cr,radius,chartob)
        self.draw_signs(cr,radius,chartob)
        self.draw_planets(cr,radius,chartob)
        self.make_plines(cr,radius,chartob,'EXT')
        self.draw_cusps(cr,radius,chartob)
        self.d_year_lines(cr,radius,chartob)
        self.d_golden_points(cr,radius,chartob)
        self.d_cross_points(cr,radius,chartob)
        self.draw_ap_aspects(cr,radius*R_ASP,chartob,self.aspmanager,self.get_AP(chartob))
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.d_inner_circles(cr,radius)

    def draw_nat(self,cr,width,height,chartob):
        chartob.__class__ = RadixChart
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        cr.translate(cx,cy)
        self.make_crown(cr,radius,chartob)

    def draw_nod(self,cr,width,height,chartob=None):
        chartob.__class__ = NodalChart
        chartob.name = 'nodal' 
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        cr.translate(cx,cy)
        self.make_crown(cr,radius,chartob)
    
    def get_AP(self,chartob):
        chart = chartob.chart
        dt = curr.date.dt
        cycles = chart.get_cycles(dt)
        dt = chartob.when_angle(cycles,get_AP_DEG(),chart)
        self.surface.dt = dt
        pe = chart.which_degree_today(dt,cycles,chartob.name)
        return pe
    
    def get_gw(self):
        return False

    def get_uni(self):
        return True

    def get_nw(self,f=None):
        return []
    
    def get_bio_AP(self,chartob):
        chart = chartob.chart
        dt = curr.date.dt
        cycles = chart.get_cycles(dt)
        dt = chartob.when_angle(cycles,get_AP_DEG(),chart)
        self.surface.dt = dt
        return dt
    
    def bio_nat(self,cr,w,h,chartob):
        chartob.__class__ = RadixChart
        self.draw_bio(cr,w,h,chartob)
    
    def bio_nod(self,cr,w,h,chartob):
        chartob.__class__ = NodalChart
        chartob.name = 'nodal'
        self.draw_bio(cr,w,h,chartob)
    
    def draw_bio(self,cr,width,height,chartob):
        global ruler
        cr.set_line_width(0.5) 
        self.minim = min(width,height)
        self.hoff = hoff = width*0.125
        self.gridw = hoff*6
        self.hroff = hoff+self.gridw
        self.voff = voff = height*0.2
        
        self.chart = chart = chartob.chart
        cp = chart.calc_cross_points()
        cph = chart.which_house(cp) 
        self.sizes = chartob.get_sizes()

        self.get_AP(chartob)
        dt = self.surface.dt
        dt = dt.combine(dt.date(),dt.time()) 
        bh,tfrac = chart.which_house_today(dt)
        ruler[0] = (hoff+self.gridw*tfrac)/width
        
        htimes = chartob.get_house_age_prog(bh) 
        self.htimes = htimes

        cycles =  chart.get_cycles(curr.date.dt)
        self.house_t = chart.house_time_lapsus(bh,cycles)
        font = pango.FontDescription(self.opts.font)
        layout = cr.create_layout()
        font.set_size(int(14*pango.SCALE*self.minim*MAGICK_FONTSCALE))
        layout.set_font_description(font)

        self.d_vert_lines(cr)
        self.d_house_number(cr,layout,bh)
        self.d_years_rule(cr,layout,htimes[0])
        if chartob.name == 'nodal':
            self.d_nodal_signbar(cr,layout,bh,chartob)
        else:
            self.d_signbar(cr,layout,bh,chartob)

        self.d_ruler(cr,width,height,voff,chartob.pe_col)
        
        self.baselines = []
        self.d_baselines(cr,layout) 
        if self.pe_zones:
            self.d_pe_zone(cr,bh,chartob)
        self.d_midpoint_line(cr,chartob) 
        mids = [t for t in htimes if t['cl'] == 'mid']
        if mids: 
            self.d_midplans(cr,layout,mids)
        
        self.intensity = [0]*72
        self.d_prev_house(cr,layout,bh,chartob)
        self.d_this_house(cr,layout,bh,chartob.name)
        self.d_follow_house(cr,layout,bh,chartob)
        
        self.d_intensity(cr,chartob)
        if bh in [cph,(cph+6)%12]:
            if bh != cph: cp = (cp+180)%360
            self.d_cross_point(cr,bh,cp,chartob)
    
    def d_ruler(self,cr,width,height,voff,pe_col): 
        cr.set_source_rgba(*(list(pe_col)+[0.5]))
        cr.arc(width*ruler[0],height*ruler[1],5,0,180*PI)
        cr.fill()
        cr.move_to(width*ruler[0],voff)
        cr.line_to(width*ruler[0],voff+voff*3)
        cr.stroke()

