# -*- coding: utf-8 -*-
import sys, os, gtk, cairo, pango, pangocairo
import PIL.Image
from .. drawing.dispatcher import PlanetManager, DrawMixin
from .. drawing.coredraw import CoreMixin
from .. drawing.planetogram import PlanetogramMixin
from .. drawing.aspects import AspectManager
import astronex.drawing.roundedcharts as roundedcharts
from .. drawing.roundedcharts import *
from .. surfaces.pngsurface import ImageExportDialog
from .. boss import boss
curr = boss.get_state()

R_ASP = 0.435
letters = ( 'd','f','h','j','k','l','g','z','x','c','v' )
alet = ( '1','2','3','4','5','6','7','6','5','4','3','2')
PDFH = 845.04685
PDFW = 597.50787 # A4 points

class PlagramWindow(gtk.Window):
    def __init__(self,parent,chart=None):
        self.boss = parent.boss
        gtk.Window.__init__(self)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_title("Planetograma")
        
        accel_group = gtk.AccelGroup()
        accel_group.connect_group(gtk.keysyms.Escape,0,gtk.ACCEL_LOCKED,self.escape)
        accel_group.connect_group(gtk.keysyms.Menu,0,gtk.ACCEL_LOCKED,self.popup_menu)
        self.add_accel_group(accel_group) 
       
        self.sda = DrawPlagram(self.boss,chart)
        self.add(self.sda)
        aux_size = int(self.boss.opts.aux_size)
        self.set_default_size(int(aux_size*1.2),aux_size)
        self.connect('destroy', self.cb_exit,parent)
        self.show_all()

    def escape(self,a,b,c,d):
        self.destroy() 

    def cb_exit(self,e,parent):
        self.boss.mainwin.plagram = None
        return False

    def popup_menu(self,acgroup,actable,keyval,mod):
        self.sda.popup_menu()

class DrawPlagram(gtk.DrawingArea):

    def __init__(self,boss,chart=None):
        self.boss = boss
        self.opts = boss.opts
        gtk.DrawingArea.__init__(self)
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | 
                gtk.gdk.BUTTON_RELEASE_MASK | 
                gtk.gdk.POINTER_MOTION_MASK | 
                gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.connect("expose_event",self.dispatch)
        self.connect("button_press_event", self.on_da_clicked)
        self.connect("button_release_event", self.on_da_clicked)
        self.connect("motion_notify_event", self.on_da_clicked)
        self.connect("scroll-event", self.on_scroll)
        self.drawer = PgMixin(boss,self) 
        self.build_menu()
        self.extended = False
        self.zoom = 1.0
        self.do_zoom = False
        self.reset = False
        self.panning = False
        self.pan_x = self.pan_y = 0

    def build_menu(self):
        self.menu = gtk.Menu()
        menu_item = gtk.MenuItem(_('Exportar a imagen'))
        self.menu.append(menu_item)
        menu_item.connect("activate", self.on_menuitem_activate)
        menu_item.show()
        menu_item = gtk.MenuItem(_('Exportar a PDF'))
        self.menu.append(menu_item)
        menu_item.connect("activate", self.on_menuitem_activate)
        menu_item.show()
        sep_item = gtk.SeparatorMenuItem()
        self.menu.append(sep_item)
        sep_item.show()
        menu_item = gtk.CheckMenuItem(_('Ver puntos de sombra'))
        self.menu.append(menu_item)
        menu_item.connect("toggled", self.on_check_toggled)
        menu_item.set_active(True)
        menu_item.show()
        menu_item = gtk.CheckMenuItem(_('Ver puntos de cambio'))
        self.menu.append(menu_item)
        menu_item.connect("toggled", self.on_check_toggled)
        menu_item.set_active(True)
        menu_item.show()
        menu_item = gtk.CheckMenuItem(_('Ver puntos de cruce'))
        self.menu.append(menu_item)
        menu_item.connect("toggled", self.on_check_toggled)
        menu_item.set_active(True)
        menu_item.show()
        menu_item = gtk.CheckMenuItem(_('Ver lineas personales'))
        self.menu.append(menu_item)
        menu_item.connect("toggled", self.on_check_toggled)
        menu_item.set_active(False)
        menu_item.show()
        menu_item = gtk.MenuItem(_('Commutar años/edad'))
        self.menu.append(menu_item)
        menu_item.connect("activate", self.on_menuitem_activate)
        menu_item.show()
    
    def popup_menu(self):
        event = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
        self.menu.popup(None, None, None, 1, event.time)
        
    def on_menuitem_activate(self,menuitem):
        if menuitem.child.get_text() == _('Exportar a imagen'):
            self.png_export()
        elif menuitem.child.get_text() == _('Commutar años/edad'):
            self.drawer.useagecircle = not self.drawer.useagecircle 
        elif menuitem.child.get_text() == _('Exportar a PDF'):
            self.pdf_export()
        self.redraw()

    def on_check_toggled(self,menuitem):
        if menuitem.child.get_text() == _('Ver puntos de sombra'):
            if menuitem.get_active():
                self.drawer.shadow = True
            else:
                self.drawer.shadow = False
        elif menuitem.child.get_text() == _('Ver lineas personales'):
            if menuitem.get_active():
                self.drawer.personlines = True
            else:
                self.drawer.personlines = False
        elif menuitem.child.get_text() == _('Ver puntos de cambio'):
            if menuitem.get_active():
                self.drawer.turnpoints = True
            else:
                self.drawer.turnpoints = False
        elif menuitem.child.get_text() == _('Ver puntos de cruce'):
            if menuitem.get_active():
                self.drawer.crosspoints = True
            else:
                self.drawer.crosspoints = False
        self.redraw()


    def on_da_clicked(self,da,event):
        info = da.get_data("move-info")
        if not info:
            info = {}
            info['button'] = -1
            da.set_data("move-info", info)

        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.extended = not self.extended
            self.reset = True
            self.redraw()
        elif event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 3:
                self.menu.popup(None, None, None, event.button, event.time)
                return True
            elif event.button == 1:
                if info['button'] < 0:
                    info['button'] = event.button
                    info['click_x'] = event.x
                    info['click_y'] = event.y
                    self.panning = True
        elif event.type == gtk.gdk.BUTTON_RELEASE:
            if info['button'] < 0: 
                return True
            if info['button'] == event.button:
                info['button'] = -1;
                self.panning = False
        elif gtk.gdk.MOTION_NOTIFY:
            if info['button'] < 0:
                return False
            x, y, state = da.window.get_pointer() # ensure more events
            x += da.allocation.x
            y += da.allocation.y
            x -= info['click_x']
            y -= info['click_y']
            self.pan_x, self.pan_y = x,y
            #self.zx, self.zy = x,y
            self.redraw()

    
    def on_scroll(self,da,event):
        if event.direction == gtk.gdk.SCROLL_UP:
            self.zoom *= 1.2
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            self.zoom = self.zoom/1.2 if self.zoom >= 1.2 else 1.0
        if self.zoom == 1.0:
            self.do_zoom = False
        else:
            self.do_zoom = True
        self.zx = event.x
        self.zy = event.y
        self.redraw()


    def dispatch(self,da,event):
        cr = self.window.cairo_create()
        w = self.allocation.width
        h = self.allocation.height
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        if self.reset: 
            self.reset = False
        else:
            if self.do_zoom:
                z = self.zoom
                cr.scale(z,z) 
                #uw,uh = cr.user_to_device(w,h)
                ux,uy = cr.user_to_device(self.zx,self.zy)
                cr.translate(self.zx-ux,self.zy-uy)
        if self.panning:
            #print (self.pan_x,self.pan_y),cr.device_to_user(self.pan_x,self.pan_y)
            cr.translate(*cr.device_to_user_distance(self.pan_x,self.pan_y))
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(self.opts.base)) 
        self.drawer.dispatch_simple(cr,w,h) 
        return False
        
    def redraw(self): 
        w = self.allocation.width
        h = self.allocation.height
        try:
            self.window.invalidate_rect(gtk.gdk.Rectangle(0,0,w,h),False)
        except AttributeError:
            pass

    def popup_menu(self):
        event = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
        self.menu.popup(None, None, None, 1, event.time)

    def png_export(self):
        dialog = ImageExportDialog(pg=True)
        filename = None
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.chooser.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        if filename is None or filename == '': return

        w = int(self.opts.hsize)
        h = int(self.opts.vsize)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        cr = pangocairo.CairoContext(cairo.Context(surface))
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(self.opts.base))
        dr = PgMixin(self.boss,self) 
        dr.dispatch_simple(cr,w,h)
        s = surface
        d = s.get_data()
        for i in xrange(0,len(d),4):
            d[i],d[i+2] = d[i+2],d[i]
        
        im = Image.frombuffer("RGBA", (s.get_width(),s.get_height()),d,"raw","RGBA",0,1)
        res = int(self.opts.resolution)
        im.info['dpi'] = (res,res)
        im.save(filename, dpi=im.info['dpi'])

        if sys.platform == 'win32':
            os.startfile(filename) 
        else: 
            os.system("%s '%s' &" % (self.opts.pngviewer,filename))

    def pdf_export(self):
        dialog = gtk.FileChooserDialog(_("Guardar..."),
                                    None,
                                    gtk.FILE_CHOOSER_ACTION_SAVE,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name(_("Documento Pdf "))
        filter.add_mime_type("application/pdf")
        filter.add_pattern("*.pdf")
        dialog.add_filter(filter)
        name = curr.curr_chart.first + "_" + "pg.pdf"
        dialog.set_current_name(name)
        if sys.platform == 'win32':
            import winshell
            dialog.set_current_folder(winshell.my_documents())
        else: 
            dialog.set_current_folder(os.path.expanduser("~"))
        dialog.set_do_overwrite_confirmation(True)

        filename = None
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        if not filename: return

        w = PDFH
        h = PDFW
        surface = cairo.PDFSurface(filename,w,h)
        surface.set_fallback_resolution(300,300)
        cr = pangocairo.CairoContext(cairo.Context(surface))
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(self.opts.base))
        dr = PgMixin(self.boss,self) 
        dr.dispatch_simple(cr,w,h)
        cr.show_page()
        surface.finish() 
        if sys.platform == 'win32':
            os.startfile(filename) 
        else: 
            os.system("%s '%s' &" % (self.opts.pdfviewer,filename))

class PgMixin(CoreMixin,PlanetogramMixin):
    def __init__(self,boss,surface=None):
        self.opts = boss.opts
        self.surface = surface
        self.shadow = True
        self.personlines = False
        self.turnpoints = True
        self.crosspoints = True
        self.useagecircle = False
        self.planetmanager = PlanetManager(self.opts.zodiac)
        roundedcharts.zodiac= self.opts.zodiac
        self.aspmanager = AspectManager(boss,self.get_gw,self.get_uni,self.get_nw,
                self.planetmanager,self.opts.zodiac.aspcolors,self.opts.base)
        CoreMixin.__init__(self,self.opts.zodiac,surface)
        PlanetogramMixin.__init__(self,self.opts.zodiac)
    
    def dispatch_simple(self,cr,w,h):
        ch1, ch2 = curr.curr_chart, curr.curr_click
        chartobject = Basic_Chart(ch1, ch2,self.planetmanager) 
        if not self.surface.extended:
            cr.translate(w/2.7,h/2)
            self.draw_planetogram(cr,w*0.7,h,chartobject)
            cr.translate(w*0.45,-h/3.2)
            self.aspmanager.unilat.lw = 0.5 * float(self.aspmanager.unilat.lw)
            self.draw_soul(cr,w/2.6,h/2.6,chartobject)
            cr.translate(0,2*h/3.2)
            self.draw_house(cr,w/2.6,h/2.6,chartobject)
            cr.translate(0,-1.4*h/3.2)
            self.lin_rulers(cr,w/7,h/4,chartobject)
            self.aspmanager.unilat.lw /=0.5 
        else:
            cr.translate(w/2,h/2)
            self.draw_planetogram(cr,w,h,chartobject)
        cr.save()
        cr.identity_matrix()
        self.draw_label(cr,w,h,chartobject)
        self.plot_cons_plan(cr,h,chartobject)
        cr.restore()

    def get_gw(self):
        return False
    
    def get_nw(self,filter):
        return None
    
    def get_uni(self):
        return True
    
    def lin_rulers(self,cr,w,h,chartob):
        hor_grid = w / 3
        ver_grid = h / 30.0
        cr.save()
        lw = cr.get_line_width()
        cr.set_line_width(0.4*lw)
        
        cr.rectangle(hor_grid*0.9,0,hor_grid*0.07,h)
        pat = cairo.LinearGradient(hor_grid,0,hor_grid,h)
        pat.add_color_stop_rgb(0.0,0,0,1)
        pat.add_color_stop_rgb(0.4,0,0.9,0)
        pat.add_color_stop_rgb(0.6,1,0.8,0)
        pat.add_color_stop_rgb(0.7,1,0,0)
        pat.add_color_stop_rgb(1.0,0,0,1)
        cr.set_source(pat)            
        cr.fill()
        
        for r in [0.92,1.12]: 
            cr.set_source_rgb(0.75,0.8,0.9)
            cr.rectangle(2*hor_grid*r,0,hor_grid*0.12,h)
            cr.fill()
            cr.set_source_rgb(0.85,0.8,0.96)
            cr.rectangle(2*hor_grid*r,ver_grid*2,hor_grid*0.12,ver_grid*25)
            cr.fill()
            cr.set_source_rgb(1.0,0.85,0.85)
            cr.rectangle(2*hor_grid*r,ver_grid*12,hor_grid*0.12,ver_grid*10)
            cr.fill()
        
        cr.set_source_rgb(0.3,0.3,0.3)

        for i in range(31):
            if i % 5 == 0:
                cr.set_line_width(0.7*lw)
            else:
                cr.set_line_width(0.4*lw)
            cr.move_to(hor_grid*0.86,i*ver_grid)
            cr.line_to(hor_grid,i*ver_grid)
            cr.stroke()
            cr.move_to(2*hor_grid*0.92,i*ver_grid)
            cr.line_to(2*hor_grid*0.98,i*ver_grid)
            cr.stroke()
            cr.move_to(2*hor_grid*1.12,i*ver_grid)
            cr.line_to(2*hor_grid*1.18,i*ver_grid)
            cr.stroke()
            if i % 5 == 0:
                if i % 10 == 0:
                    font_size = 12.0 * w * 0.004
                    self.set_font(cr,font_size,bold=True)
                else:
                    font_size = 10.0 * w * 0.004
                    self.set_font(cr,font_size)
                _, _, ww, hh, _, _ = cr.text_extents(str(i))
                cr.move_to((2*hor_grid*1.05)-ww/1.8,(h-i*ver_grid)+hh/2)
                cr.show_text(str(i))

        cr.set_source_rgb(0.4,0.4,0.4)
        cr.move_to(2*hor_grid*0.92,0)
        cr.line_to(2*hor_grid*0.92,h)
        cr.set_line_width(0.5*lw)
        cr.stroke()
        cr.move_to(2*hor_grid*0.95,0)
        cr.line_to(2*hor_grid*0.95,h)
        cr.set_line_width(0.4*lw)
        cr.stroke()

        cr.set_source_rgb(0.4,0.4,0.4)
        cr.move_to(2*hor_grid*1.15,0)
        cr.line_to(2*hor_grid*1.15,h)
        cr.set_line_width(0.4*lw)
        cr.stroke()
        cr.move_to(2*hor_grid*1.18,0)
        cr.line_to(2*hor_grid*1.18,h)
        cr.set_line_width(0.5*lw)
        cr.stroke()

        chartob.__class__ = RadixChart
        plan =  [ p % 30.0 for p in chartob.get_planets() ]
        plan = sorted([ (p,i) for i,p in enumerate(plan) ])
        fac = [0.7,1.2]
        plan = self.inject(plan,fac)
        layout = cr.create_layout()
        font = pango.FontDescription("Astro-Nex")
        font.set_size(int(11*pango.SCALE*w*0.007))
        layout.set_font_description(font)
        cr.set_source_rgb(0.2,0.2,0.2)
        for i,p in enumerate(plan):
            deg = p.deg - p.corr
            layout.set_text(letters[i])
            ink,logical = layout.get_extents()
            ww = logical[2]/pango.SCALE
            hh = logical[3]/pango.SCALE
            cr.move_to((2*hor_grid*0.25*p.fac)-ww/2,(h-deg*ver_grid)-hh/2)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()
            #fac[0],fac[1] = fac[1],fac[0]  
            cr.move_to(2*hor_grid*0.4,h-p.deg*ver_grid)
            cr.line_to(2*hor_grid*0.44,h-p.deg*ver_grid)
            cr.stroke()
        nplan = self.nodal_lin_planets(chartob)
        plan = sorted([ (p,i) for i,p in enumerate(nplan) ])
        fac = [0.9,1.1]
        plan = self.inject(plan,fac)
        cr.set_source_rgb(0.43,0.0,0.78)
        for i,p in enumerate(plan):
            deg = p.deg - p.corr
            layout.set_text(letters[i])
            ink,logical = layout.get_extents()
            ww = logical[2]/pango.SCALE
            hh = logical[3]/pango.SCALE
            cr.move_to((2*hor_grid*0.7*p.fac)-ww/2,(h-deg*ver_grid)-hh/2)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()
            fac[0],fac[1] = fac[1],fac[0]  
            cr.move_to(2*hor_grid*0.87,h-p.deg*ver_grid)
            cr.line_to(2*hor_grid*0.92,h-p.deg*ver_grid)
            cr.stroke()
        chartob.__class__ = SoulChart
        splan = [ p % 30.0 for p in chartob.get_planets() ]
        plan = sorted([ (p,i) for i,p in enumerate(splan) ])
        fac = [0.95,1.05]
        plan = self.inject(plan,fac)
        cr.set_source_rgb(0.76,0.0,1.0)
        for i,p in enumerate(plan):
            deg = p.deg - p.corr
            layout.set_text(letters[i])
            ink,logical = layout.get_extents()
            ww = logical[2]/pango.SCALE
            hh = logical[3]/pango.SCALE
            cr.move_to((2*hor_grid*1.45*p.fac)-ww/2,(h-deg*ver_grid)-hh/2)
            cr.layout_path(layout)
            cr.fill()
            cr.new_path()
            fac[0],fac[1] = fac[1],fac[0]  
            cr.move_to(2*hor_grid*1.18,h-p.deg*ver_grid)
            cr.line_to(2*hor_grid*1.23,h-p.deg*ver_grid)
            cr.stroke()
        cr.restore()

    def draw_soul(self,cr,width,height,chartob=None):
        chartob.__class__ = SoulChart 
        chartob.name = 'soul' 
        offset = chartob.get_offset()
        cx,cy = width/2,height/2
        radius = min(cx,cy)
        
        cr.save()
        cr.set_line_width(cr.get_line_width()*0.6)
        self.set_plots(chartob)
        cr.scale(1.4,1.4)
        #self.d_lonely_cusp(cr,radius,chartob)
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.draw_planets(cr,radius,chartob)
        self.make_small_ruler(cr,radius,offset)
        cr.restore()
    
    def draw_house(self,cr,width,height,chartob=None):
        chartob.__class__ = HouseChart
        chartob.set_iter_sizes()
        offset = chartob.get_offset()
        cx,cy = width/2,height/2
        radius = min(cx,cy)
    
        cr.save()
        cr.set_line_width(cr.get_line_width()*0.6)
        self.set_plots(chartob)
        cr.scale(1.4,1.4)
        self.aspmanager.manage_aspects(cr,radius*R_ASP,chartob.get_planets())
        self.make_plines(cr,radius,chartob,'INN')
        self.draw_planets(cr,radius,chartob)
        self.make_small_ruler(cr,radius,offset)
        cr.restore()
    
    def make_small_ruler(self,cr,radius,offset):
        rules = [0.015,0.010,0.005]
        insets = [radius * i for i in rules]
        radius = radius * 0.48
        
        default = insets.pop()
        insets = dict(zip((0,5),insets))
        cr.save()
        cr.set_source_rgb(0,0,0)
        cr.set_line_width(0.5*cr.get_line_width())
        for i in xrange(360):
            angle = (offset+i) * RAD
            inset = radius - insets.get(i%10,default)
            self.d_radial_line(cr,radius,inset,angle)
        
        cr.set_source_rgb(1,1,1)
        cr.arc(0,0,radius*0.15,0,360*RAD)
        cr.fill_preserve()
        cr.set_source_rgb(0,0,0)
        cr.set_line_width(0.5*cr.get_line_width())
        cr.stroke()
        cr.arc(0,0,radius/90,0,360*RAD)
        cr.fill()
        cr.restore()

    def plot_cons_plan(self,cr,h,chartob):
        chartob.__class__ = RadixChart
        dplan =  [ p % 30.0 for p in chartob.get_planets() ]
        plan = sorted([ (p,i) for i,p in enumerate(dplan) ])
        asc =   chartob.chart.houses[0] % 30.0
        diffs = []
        for p in plan:
            d = p[0]-asc
            if d < -15.0:
                d += 30.0
            elif d > 15.0:
                d = 30.0 - d
            diffs.append((d,p[1]))
        diffs = sorted(diffs,key=lambda x: abs(x[0]))
        asc =   chartob.chart.houses[0]
        dplan =  chartob.get_planets()
        wit = diffs[0][0]
        cons = []
        for i,p in enumerate(diffs):
            deg = dplan[p[1]]
            a = int(round(abs(asc-deg)/30.0))
            if abs(p[0] - wit) <= 1.0:
                cons.append((a,p[1]))
                #cons.append((a,p))
                wit = p[0]
            else:
                break
            if i >= 2:
                break
        layout = cr.create_layout()
        font = pango.FontDescription("Astro-Nex")
        font.set_size(14*pango.SCALE)
        layout.set_font_description(font)
        cr.save()
        cr.set_source_rgb(1.0,0.1,1.0) 
        for i,c in enumerate(cons):
            label = "%s%s" % (alet[c[0]],letters[c[1]])
            layout.set_text(label)
            cr.move_to(22,(h-110)+24*i)
            cr.show_layout(layout)
        cr.restore()
    
    def draw_label(self,cr,w,h,chartob): 
        chart  = chartob.chart
        layout = cr.create_layout()
        font = pango.FontDescription(self.opts.font)
        font.set_size(12*pango.SCALE)
        layout.set_font_description(font)
        cr.save()
        cr.set_source_rgb(0,0.7,0.1) 
        name = "%s %s" % (chart.first,chart.last) 
        layout.set_text(name)
        cr.move_to(20,h-25)
        cr.show_layout(layout)
        cr.restore()
    
    def nodal_lin_planets(self,chartob,plot="plot1"):
        cusps = chartob.get_cusps_offsets()
        asc =   chartob.chart.houses[0]
        cusps = [ c % 360 for c in cusps ] 
        sizes = chartob.get_sizes()
        chartob.__class__ = NodalChart
        plots = self.set_plots(chartob,plot)
        degs = []
        for plot in plots:
            plot.degree %= 360.0
            h = (5 - int(plot.degree/30)) % 12
            dist = 30.0 - plot.degree % 30.0
            degree = (cusps[h] - dist*sizes[h]/30.0) % 360
            degree = (180 + asc - degree) % 360
            degs.append(degree % 30)
        return degs
            
    def marshall(self,plans):
        '''Partition planets too close in groups'''
        def diftuple(tuple):
            d = tuple[1][0] - tuple[0][0]
            if d < 0: d += 360
            return d <= 3
        
        planque = deque(plans) 
        boolque = deque([diftuple(t) for t in izip(plans,plans[1:]+[plans[0]])])
        if True in boolque:
            while boolque[0] != True or boolque[-1] != False:
                boolque.rotate(-1)
                planque.rotate(-1) 

        jail = []; cell = set()
        for low,btuple in izip(planque,boolque):
            cell.add((low[0],low[1])) 
            if btuple is False: 
                jail.append(cell)
                cell = set()
        return jail
    
    def inject(self,plan,facs):
        jail = self.marshall(plan)
        plots = [None] * 11
        class plot_obj(object): pass
        for cell in jail:
            name = self.__class__.__name__
            num_plans = len(cell)
            fac = facs[:]
            gen_corr = 1.5
            witness = sorted(cell)
            for pos,pl in enumerate(witness):
                po = plot_obj()
                po.deg= pl[0]
                if num_plans < 2:
                    po.fac = 1.0
                else: 
                    po.fac = fac[0]
                    fac[0],fac[1] = fac[1],fac[0]
                if num_plans < 3:
                    po.corr = 0.0
                else: 
                    faraway = pos - (num_plans // 2)
                    if faraway < 0:
                        diff = dif(pl[0],witness[pos+1][0])
                    elif faraway > 0:
                        diff = dif(witness[pos-1][0],pl[0]) 
                        if diff >= 353.5: 
                            diff = -(diff - 353.5)
                    po.corr = -faraway * (gen_corr - diff)/2.5 
                plots[pl[1]] = po 
        return plots
