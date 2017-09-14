# -*- coding: utf-8 -*-
import gtk
import cairo
import pango
import math
from math import pi as PI
from collections import deque
from copy import copy
from datetime import datetime
from .. drawing.dispatcher import DrawMixin
from .. drawing.diagrams import DiagramMixin
from .. drawing.biograph import _bio
from .. utils import parsestrtime
from .. boss import boss
curr = boss.get_state()

RAD = PI/ 180

class DrawDiagram(gtk.DrawingArea):
    opdia = deque(['dyn_bars','dyn_energy','dyn_differences','dyn_houses','dyn_signs'])
    def __init__(self,boss):
        self.boss = boss
        self.opts = boss.opts
        gtk.DrawingArea.__init__(self)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | 
                gtk.gdk.BUTTON_RELEASE_MASK | 
                gtk.gdk.POINTER_MOTION_MASK | 
                gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.connect("expose_event",self.dispatch)
        self.connect("button_press_event", self.on_diada_clicked)        
        self.connect("scroll-event", self.on_scroll)
        self.drawer = DiagramMixin(boss.opts.zodiac) 

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
        
        getattr(self.drawer,self.opdia[0])(cr,w,h) 
        return True

    def on_scroll(self,da,event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.opdia.rotate(1)
        else:
            self.opdia.rotate(-1)
        self.redraw()
        return True

    def on_diada_clicked(self,hs,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            boss.mpanel.toolbar.get_nth_item(5).set_active(False)
        return True
    
    def redraw(self): 
        w = self.allocation.width
        h = self.allocation.height
        self.window.invalidate_rect(gtk.gdk.Rectangle(0,0,w,h),False)

#################################################
crcol = ['card','fix','mut']
crosscolsalpha = [(0.7,0,0.2,0.7),(0.1,0.1,0.6,0.7),(0,0.6,0.1,0.7)]
crosscols = [(0.7,0,0.2),(0.1,0.1,0.6),(0,0.6,0.1)]
_h = -1
prev_chart = None

class HouseSelector(gtk.DrawingArea):
    def __init__(self,boss):
        global prev_chart
        self.boss = boss
        self.opts = boss.opts
        gtk.DrawingArea.__init__(self)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | 
                gtk.gdk.BUTTON_RELEASE_MASK | 
                gtk.gdk.POINTER_MOTION_MASK | 
                gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.connect("expose_event",self.dispatch)
        self.connect("button_press_event", self.on_hs_clicked)        
        self.connect("scroll-event", self.on_scroll)
        try:
            prev_chart = curr.curr_chart,curr.curr_chart.first,curr.curr_op 
        except AttributeError:
            pass
    
    def set_house_from_date(self,dt):
        global _h
        _bio, frac = curr.curr_chart.which_house_today(dt)
        _h = _bio
        self.queue_draw()
        self.parent.parent.drawer.set_bio_from_date(_bio,frac)

    def on_hs_clicked(self,hs,event):
        global _h
        if curr.curr_chart == curr.now:
            return True
        x, y = event.x,event.y
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.parent.parent.panel.nowbut.emit('clicked')
            _h = -1
            self.queue_draw()
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            w = hs.allocation.width/2; h = hs.allocation.height/2
            deg = math.degrees(math.atan2(y-h,x-w))
            _h = int(math.ceil(5 - (deg/30)))
            self.queue_draw()
            self.parent.parent.drawer.set_bio(_h,None)
        return True

    def dispatch(self,da,event):
        global _h,prev_chart
        cr = self.window.cairo_create()
        w = self.allocation.width
        h = self.allocation.height
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgb(1.0,0.9,0.65)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(self.opts.base))
        
        cr.translate(w/2,h/2)
        r =min(w/2,h/2)
        ro = r*0.8
        ri = r*0.4
        rm = r*0.6
        cr.set_source_rgb(0,0,0.8)
        cr.arc(0,0,r*0.08,0,180*PI) 
        cr.fill()
        pointcol = (0.9,0.8,0.6)
        cr.set_source_rgb(*pointcol)
        cr.arc(0,0,r*0.03,0,180*PI) 
        cr.fill()
        for ang in range(0,360,30):
            ix = (ang/30)%3
            a = 180 - ang
            cr.set_source_rgba(*crosscols[ix])
            cr.move_to(ri*math.cos(a*RAD),ri*math.sin(a*RAD))
            cr.line_to(ro*math.cos(a*RAD),ro*math.sin(a*RAD))
            cr.arc_negative(0,0,ro,a*RAD,(a-30)*RAD)
            cr.line_to(ri*math.cos((a-30)*RAD),ri*math.sin((a-30)*RAD))
            cr.arc(0,0,ri,(a-30)*RAD,a*RAD)
            cr.fill()

        this_chart = curr.curr_chart,curr.curr_chart.first,curr.curr_op
        if this_chart[1] != prev_chart[1]: 
            _h = -1

        if this_chart != prev_chart: 
            prev_chart = this_chart 

        if _h < 0:
            _h,_ = curr.curr_chart.which_house_today(datetime.now())

        cr.set_source_rgb(*pointcol)
        x = rm*math.cos((165-_h*30)*RAD)
        y = rm*math.sin((165-_h*30)*RAD)
        cr.move_to(0,0)
        cr.line_to(x,y)
        cr.stroke()
        cr.arc(x,y,5,0,180*PI)
        cr.fill()
        return True

    def on_scroll(self,hs,event):
        global _h
        if curr.curr_chart == curr.now:
            return True
        if event.direction == gtk.gdk.SCROLL_UP:
            _h = (_h - 1)%12
        else:
            _h = (_h + 1)%12
        self.queue_draw()
        self.parent.parent.drawer.set_bio(_h,None)
        return True

    def house_updown(self,amount):
        global _h
        _h = (_h + amount)%12
        self.queue_draw()
        self.parent.parent.drawer.set_bio(_h,None)

    def redraw(self): 
        w = self.allocation.width
        h = self.allocation.height
        self.window.invalidate_rect(gtk.gdk.Rectangle(0,0,w,h),False)

##################################################
opcharts = ['draw_nat', 'draw_house',
        'draw_nod','draw_soul','draw_dharma','draw_ur_nodal','draw_local','draw_prof', 'draw_int', 'draw_single', 'draw_radsoul']
opclicks = ['click_hh', 'click_nn', 'click_hn', 'click_nh','click_ss','click_rr','click_rs','click_sn','subject_click']
opdia = ['dyn_bars','dyn_energy','dyn_differences','dyn_houses','dyn_signs']
opbio = ['bio_nat','bio_nod','bio_soul','bio_dharma']
optrans = ['draw_transits','sec_prog','solar_rev']
opcoup = [ 'ascent_star','wundersensi_star','polar_star','crown_comp','paarwabe_plot','comp_pe'] 
tradtrans = {'draw_transits': _('Transitos'),'sec_prog': _('Progresion secundaria'), 'solar_rev':_('Revolucion solar')}
initmenu = (_('Congelar'),_('Permutar'),_('Cartas'),'Clics',_('DDiagramas'),_('Biografias'),_('Parejas'),_('Transitos'))

class DrawAux(gtk.DrawingArea):
    pepending = [False,None,None]

    def __init__(self,boss,chart=None):
        self.boss = boss
        self.opts = boss.opts
        self.opcharts = deque(opcharts)
        self.opclicks = deque(opclicks)
        self.opdia = deque(opdia)
        self.opbio = deque(opbio)
        self.opcoup = deque(opcoup)
        self.optrans = deque(optrans)
        self.opaux = self.opcharts
        gtk.DrawingArea.__init__(self)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | 
                gtk.gdk.BUTTON_RELEASE_MASK | 
                gtk.gdk.POINTER_MOTION_MASK | 
                gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.connect("expose_event",self.dispatch)
        self.connect("button_press_event", self.on_da_clicked)
        self.connect("scroll-event", self.on_scroll)
        self.drawer = DrawMixin(boss.opts,self) 
        self.menu = gtk.Menu()
        for buf in initmenu:
            menu_item = gtk.MenuItem(buf)
            self.menu.append(menu_item)
            menu_item.connect("activate", self.on_menuitem_activate)
            menu_item.show()
        sep_item = gtk.SeparatorMenuItem()
        self.menu.insert(sep_item,2)
        sep_item.show()
        if chart:
            self.cache = [copy(chart),copy(curr.curr_click)] 
            self.frozen = True
        else:
            self.cache = [copy(curr.curr_chart),copy(curr.curr_click)] 
            self.frozen = False
        self.permuted = False
        

    def dispatch(self,da,event):
        cr = self.window.cairo_create()
        w = self.allocation.width
        h = self.allocation.height
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(self.opts.base))
        
        if not self.frozen:
            self.cache = [copy(curr.curr_chart),copy(curr.curr_click)] 
            if self.permuted:
                self.cache[0],self.cache[1] = self.cache[1],self.cache[0]
        self.drawer.dispatch_simple(cr,w,h,self.opaux[0],self.cache[0],self.cache[1]) 
        if self.opaux == self.optrans or self.cache[0].first == _("Momento actual"):
            self.d_now_date(cr,w,h)
        if self.pepending[0]:
            self.draw_pelabel(cr,w,h)
            self.pepending = [False,None,None]
        self.draw_label(cr,w,h) 
        return False
        
    def on_scroll(self,da,event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.opaux.rotate(1)
        else:
            self.opaux.rotate(-1)
        self.redraw()
        return True

    def redraw(self): 
        w = self.allocation.width
        h = self.allocation.height
        self.window.invalidate_rect(gtk.gdk.Rectangle(0,0,w,h),False)

    def popup_menu(self):
        event = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
        self.menu.popup(None, None, None, 1, event.time)

    def on_da_clicked(self,da,event):
        x, y = event.x,event.y
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.menu.popup(None, None, None, event.button, event.time)
            return True
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            if self.opaux == self.opbio:
                return False
            if self.opaux == self.opcharts:
                rad = list(self.opaux).index('draw_nat')
            elif self.opaux == self.opclicks:
                rad = list(self.opaux).index('click_hh')
            elif self.opaux == self.opdia:
                rad = list(self.opaux).index('dyn_bars')
            else:
                rad = 0
            self.opaux.rotate(-rad)
            self.redraw()
            return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            if self.opaux == self.opbio:
                return False
            if not self.drawer.get_showAP() or self.opaux != self.opcharts :
                return True 
            w = da.allocation.width/2; h = da.allocation.height/2
            deg = math.degrees(math.atan2(y-h,x-w))
            for_ch = ['chart','click'][self.permuted]
            self.drawer.set_AP(deg,self.opaux[0],for_ch)
            self.boss.da.redraw()
            self.boss.da.redraw_auxwins()
            if curr.curr_op in ['bio_nat','bio_nod','bio_soul']:
                dt = curr.date.dt
                dt = datetime.combine(dt.date(),dt.time())
                boss.da.hsel.child.set_house_from_date(dt)
            return True

    def on_menuitem_activate(self,menuitem): 
        if menuitem.child.get_text() == _('Descongelar'):
            self.frozen = False
            menuitem.child.set_text(_('Congelar'))
        elif menuitem.child.get_text() == _('Congelar'):
            self.frozen = True
            menuitem.child.set_text(_('Descongelar')) 
        elif menuitem.child.get_text() == _('Permutar'):
            self.cache[0],self.cache[1] = self.cache[1],self.cache[0]
            self.permuted = not self.permuted
        elif menuitem.child.get_text() == 'Clics':
            self.opaux = self.opclicks
        elif menuitem.child.get_text() == _('DDiagramas'):
            self.opaux = self.opdia
        elif menuitem.child.get_text() == _('Cartas'):
            self.opaux = self.opcharts
        elif menuitem.child.get_text() == _('Transitos'):
            self.opaux = self.optrans
        elif menuitem.child.get_text() == _('Parejas'):
            self.opaux = self.opcoup
        elif menuitem.child.get_text() == _('Biografias'):
            self.opaux = self.opbio
        self.redraw()
        return True

    def draw_label(self,cr,w,h): 
        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        
        cols = [(0,0,0.4),(0.8,0,0.1)]
        if self.permuted:
            cols[1],cols[0] = cols[0],cols[1]

        ix = [0,1][self.opaux in [self.opclicks,self.opcoup]]
        fac = [1,2][self.opaux == self.opdia or self.opaux == self.opbio or self.opaux[0] == 'comp_pe']
        h = (fac*h/2)-15
        if self.opaux[0] == 'comp_pe':
            signfac = 0
        else:
            signfac = -1

        for i in range(ix+1):
            name = "%s %s" % (self.cache[i].first,self.cache[i].last) 
            layout.set_text(name)
            ink,logical = layout.get_extents()
            xpos = logical[2]/pango.SCALE
            if ix and not i:
                pos = signfac*(fac*w/2)+5
            else:
                pos = (fac*w/2) - xpos - 5 
            cr.set_source_rgb(*cols[i]) 
            cr.move_to(pos,h)
            cr.show_layout(layout)

        if self.opaux == self.optrans:
            layout.set_text(tradtrans[self.opaux[0]])
            ink,logical = layout.get_extents()
            cr.move_to(5-w/2,h)
            cr.show_layout(layout)


    def d_now_date(self,cr,w,h):
        strdate = curr.charts['now'].date
        date,time = parsestrtime(strdate)
        date = date + " " + time.split(" ")[0]
        layout = cr.create_layout()
        cr.set_source_rgb(0,0,0.6)
        font = pango.FontDescription(self.opts.font)
        font.set_size(8*pango.SCALE)
        layout.set_font_description(font)
        layout.set_text(date)
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to((w/2)-xpos-5,(-h/2)+5) 
        cr.show_layout(layout)
    
    def d_tr_label(self,cr,w,h):
        pass

    def draw_pelabel(self,cr,w,h):
        pe = self.pepending[1]
        sign,deg = divmod(pe,30)
        mint = int((deg - int(deg)) * 60)
        sign = int(sign)
        deg = int(deg)
        let = self.drawer.zodlet[sign]
        col = boss.opts.zodiac.zod[sign].col
        sign = u"%s\u00b0 %s\u00b4" % (deg,mint)
        
        iambio = (self.opaux == self.opbio)
        h = -([1,0][iambio]*h/2)+5
        w = ([1,2][iambio]*w/2)-5

        layout = cr.create_layout()
        cr.set_source_rgb(*col)
        font = pango.FontDescription("Astro-Nex")
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        layout.set_text(let)
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        cr.move_to(w-xpos,h) 
        cr.show_layout(layout)
        
        cr.set_source_rgb(0,0,0.6) 
        font = pango.FontDescription(self.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        layout.set_text(sign)
        ink,logical = layout.get_extents()
        xpos += logical[2]/pango.SCALE
        cr.move_to(w-xpos,h) 
        cr.show_layout(layout)
