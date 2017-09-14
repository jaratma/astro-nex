# -*- coding: utf-8 -*-
import gtk
import pango
from .. drawing.paarwabe import ascent_texts, wunder_texts, polar_texts
from .. boss import boss
curr = boss.get_state()

textops = ['text_for_ascent','text_for_wunder', 'text_for_polar']


class PlanPopup(gtk.Window):
    def __init__(self,boss):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.KEY_PRESS_MASK )
        #self.set_transient_for(boss.mainwin)
        self.connect('button-press-event', self.on_button_press)
        self.connect('key-press-event', self.on_key_press_event) 
        area = PetitArea(boss.opts.zodiac)
        self.add(area)
        self.set_default_size(115,195)
        self.set_position(gtk.WIN_POS_MOUSE)
        self.show_all()

    def on_button_press(self,a,event):
        boss.da.planpopup = None
        self.destroy() 
    
    def on_key_press_event(self,window,event): 
        if event.keyval == gtk.keysyms.Escape: 
            boss.da.planpopup = None
            self.destroy() 
        return False

class PetitArea(gtk.DrawingArea):
    zodlet = ( 'q','w','e','r','t','y','u','i','o','p','a','s' )
    planlet = [ 'd','f','h','j','k','l','g','z','x','c','v' ]
    def __init__(self,zodiac):
        self.zod = zodiac.zod
        self.plan = zodiac.plan
        gtk.DrawingArea.__init__(self)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | 
                gtk.gdk.BUTTON_RELEASE_MASK ) 
        self.connect("expose_event",self.dispatch)

    def dispatch(self,da,event):
        cr = self.window.cairo_create()
        w = self.allocation.width
        h = self.allocation.height
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgb(0.96,0.96,0.99)
        cr.rectangle(0,0,w,h)
        cr.fill()
        self.data_planh(cr)
        return True
    
    def data_planh(self,cr):
        cr.set_source_rgb(0,0,0.4)
        layout = cr.create_layout()
        if curr.curr_op == 'draw_transits':
            chart = curr.now
        else:
            chart = curr.curr_chart
        #signs = chart.which_all_signs()
        signs = chart.calc_plan_with_retrogression(boss.state.epheflag)
        
        font = pango.FontDescription("Astro-Nex")
        font.set_size(11*pango.SCALE)
        layout.set_font_description(font)
        for i in range(11):
            cr.move_to(10,10+i*16)
            colp = self.plan[i].col
            cr.set_source_rgb(*colp) 
            text ="%s" % self.planlet[i]
            layout.set_text(text)
            cr.show_layout(layout)
            cr.new_path()
            
        cr.set_source_rgb(0,0,0.4)
        font = pango.FontDescription(boss.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        for i in range(11):
            cr.move_to(30,10+i*16)
            text = signs[i]['deg']
            layout.set_text(text)
            cr.show_layout(layout)
            cr.new_path()

        font = pango.FontDescription("Astro-Nex")
        font.set_size(11*pango.SCALE)
        layout.set_font_description(font)
        for i in range(11):
            cr.move_to(86,10+i*16)
            col = self.zod[signs[i]['col']%4].col
            text ="%s" % (self.zodlet[signs[i]['name']])
            cr.set_source_rgb(*col) 
            layout.set_text(text)
            cr.show_layout(layout)
            cr.new_path()

        cr.set_source_rgb(0,0,0.4)
        font = pango.FontDescription(boss.opts.font)
        font.set_size(9*pango.SCALE)
        layout.set_font_description(font)
        text = 'r'
        for i in range(11):
            if signs[i]['speed'] < 0:
                cr.move_to(72,10+i*16)
                layout.set_text(text)
                cr.show_layout(layout)
                cr.new_path()

################################################
class TextPopup(gtk.Window):
    def __init__(self,index):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.on_button_press)
        area = TextArea(index)
        self.add(area)
        self.set_default_size(420,200)
        self.set_position(gtk.WIN_POS_MOUSE)
        self.show_all()

    def on_button_press(self,a,event):
        boss.da.textspopup = None
        self.destroy() 
    
    def on_key_press_event(self,window,event): 
        if event.keyval == gtk.keysyms.Escape: 
            boss.da.planpopup = None
            self.destroy() 
        return False


class TextArea(gtk.DrawingArea):
    def __init__(self,index):
        self.index = index
        gtk.DrawingArea.__init__(self)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | 
                gtk.gdk.BUTTON_RELEASE_MASK ) 
        self.connect("expose_event",self.dispatch,index)


    def dispatch(self,da,event,index):
        cr = self.window.cairo_create()
        w = self.allocation.width
        h = self.allocation.height
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgb(0.9,0.96,0.9)
        cr.rectangle(0,0,w,h)
        cr.fill_preserve()
        cr.set_source_rgb(0.4,0.6,0.4)
        cr.set_line_width(3)
        cr.stroke()
        getattr(self,textops[index-2])(cr,w)
        return True
    
    def text_for_ascent(self,cr,width):
        v = width*0.05
        fem_col = (0,0.2,0.6)
        mas_col = (0.7,0,0)
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(10*pango.SCALE)
        layout.set_font_description(font)
        cr.translate(6,6)
        
        cr.set_source_rgb(*mas_col)
        layout.set_text("1  %s" % ascent_texts['a1'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,0)
        cr.show_layout(layout)
        layout.set_text("2  %s" % ascent_texts['a2'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v)
        cr.show_layout(layout)
        layout.set_text("3  %s" % ascent_texts['a3'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*2)
        cr.show_layout(layout)
        layout.set_text("%s" % ascent_texts['a3b'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*3)
        cr.show_layout(layout)
        layout.set_text("4  %s" % ascent_texts['a4'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*4)
        cr.show_layout(layout)
        layout.set_text("%s" % ascent_texts['a4b'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*5)
        cr.show_layout(layout)
        cr.set_source_rgb(*fem_col)
        layout.set_text("5/6  %s" % ascent_texts['a5'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*6)
        cr.show_layout(layout)
        layout.set_text("7/8  %s" % ascent_texts['a7'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*7)
        cr.show_layout(layout)

    def text_for_polar(self,cr,width):
        r = width/2
        v = r*0.05
        pol_col = (0,0.7,0)
        fem_col = (0,0.2,0.6)
        mas_col = (0.7,0,0)
        
        cr.translate(r,0)
        r *= 0.9
        cr.set_source_rgb(1.0,1,0.8)
        cr.rectangle(-r*1.05,10.2*v*0.97,2*r*1.05,6*v)
        cr.fill()
        
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(10*pango.SCALE)
        layout.set_font_description(font)

        layout.set_text("6  %s" % polar_texts['P6'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(-r,1.5*v-h/2)
        cr.set_source_rgb(*mas_col)
        cr.show_layout(layout)

        layout.set_text("5 %s" % polar_texts['P5'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w,1.5*v-h/2)
        cr.set_source_rgb(*mas_col)
        cr.show_layout(layout)

        layout.set_text("14  %s" % polar_texts['P14'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2,3*v-h/2)
        cr.set_source_rgb(*pol_col)
        cr.show_layout(layout)

        layout.set_text("9  %s" % polar_texts['P9'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(-r,4.5*v-h/2)
        cr.set_source_rgb(*fem_col)
        cr.show_layout(layout)

        layout.set_text("10  %s" % polar_texts['P10'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w,4.5*v-h/2)
        cr.set_source_rgb(*fem_col)
        cr.show_layout(layout)

        layout.set_text("13  %s" % polar_texts['P13'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2,6*v-h/2)
        cr.set_source_rgb(*pol_col)
        cr.show_layout(layout)

        layout.set_text("4  %s" % polar_texts['P4'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(-r,7.5*v-h/2)
        cr.set_source_rgb(*mas_col)
        cr.show_layout(layout)

        layout.set_text("3  %s" % polar_texts['P3'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w,9*v-h/2)
        cr.set_source_rgb(*mas_col)
        cr.show_layout(layout)

        layout.set_text("12  %s" % polar_texts['P12'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2,10.5*v-h/2)
        cr.set_source_rgb(*pol_col)
        cr.show_layout(layout)

        layout.set_text("7  %s" % polar_texts['P7'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(-r,12*v-h/2)
        cr.set_source_rgb(*fem_col)
        cr.show_layout(layout)
        
        layout.set_text("8  %s" % polar_texts['P8'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w,12*v-h/2)
        cr.set_source_rgb(*fem_col)
        cr.show_layout(layout)

        layout.set_text("11  %s" % polar_texts['P11'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(-w/2,13.5*v-h/2)
        cr.set_source_rgb(*pol_col)
        cr.show_layout(layout)

        layout.set_text("2 %s" % polar_texts['P2'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(-r,15*v-h/2)
        cr.set_source_rgb(*fem_col)
        cr.show_layout(layout)
        
        layout.set_text("1 %s" % polar_texts['P1'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(r-w,15*v-h/2)
        cr.set_source_rgb(*mas_col)
        cr.show_layout(layout)


    def text_for_wunder(self,cr,width):
        v = width*0.045
        mar = 12
        w_col = (0.6,0,0.6)
        s_col = (0,0.6,0.2)
        layout = cr.create_layout()
        font = pango.FontDescription(boss.opts.font)
        font.set_size(10*pango.SCALE)
        font.set_weight(pango.WEIGHT_NORMAL)
        font.set_style(pango.STYLE_NORMAL)
        layout.set_font_description(font)

        cr.translate(6,6)
        
        cr.set_source_rgb(*w_col)
        layout.set_text("1  %s" % wunder_texts['w1'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,0)
        cr.show_layout(layout)
        layout.set_text("2  %s" % wunder_texts['w2'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v)
        cr.show_layout(layout)
        layout.set_text("3  %s" % wunder_texts['w3'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*2)
        cr.show_layout(layout)
        layout.set_text("4  %s" % wunder_texts['w4'])
        ink,logical = layout.get_extents()
        h = logical[3]/pango.SCALE
        cr.move_to(0,v*3)
        cr.show_layout(layout)
        cr.set_source_rgb(*s_col)
        layout.set_text("1  %s" % wunder_texts['s1'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width-mar-w,v*4)
        cr.show_layout(layout)
        layout.set_text("2  %s" % wunder_texts['s2'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width-mar-w,v*5)
        cr.show_layout(layout)
        layout.set_text("3  %s" % wunder_texts['s3'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width-mar-w,v*6)
        cr.show_layout(layout)
        layout.set_text("4  %s" % wunder_texts['s4'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width-mar-w,v*7)
        cr.show_layout(layout)
        layout.set_text("5  %s" % wunder_texts['s5'])
        ink,logical = layout.get_extents()
        w = logical[2]/pango.SCALE
        h = logical[3]/pango.SCALE
        cr.move_to(width-mar-w,v*8)
        cr.show_layout(layout)
