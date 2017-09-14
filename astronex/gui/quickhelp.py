# -*- coding: utf-8 -*-
import os
import gtk, gobject
import cairo, pango
from .. extensions.path import path

boss = None

class HelpWindow(gtk.Window):
    def __init__(self,parent):
        global boss
        boss = parent.boss
        gtk.Window.__init__(self)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_resizable(False)
        self.set_title(_("Ayuda"))

        accel_group = gtk.AccelGroup()
        accel_group.connect_group(gtk.keysyms.Escape,0,gtk.ACCEL_LOCKED,self.escape)
        self.add_accel_group(accel_group) 

        self.da = DrawHelp()
        self.add(self.da)

        self.set_default_size(710,500)
        self.connect('destroy', self.cb_exit,parent)
        self.show_all()

    def escape(self,a,b,c,d):
        self.destroy() 

    def cb_exit(self,e,parent):
        #self.boss.da.auxwins.remove(self)
        return False


class DrawHelp(gtk.DrawingArea):
    background = None
    back_width  = 0
    back_height = 0

    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.set_size_request(710,500) 
        self.connect("expose_event",self.dispatch)
        self.connect("button-press-event",self.dispatch)
        self.surface = self.load_pixbufs()        
    
    def load_pixbufs(self):
        appath = boss.app.appath 
        appath = path.joinpath(appath,'astronex')
        imgfile = path.joinpath(appath,"resources/saturn-soft.png")
        return cairo.ImageSurface.create_from_png(imgfile)

    def dispatch(self,da,event):
        cr = self.window.cairo_create()
        cr.set_source_surface(self.surface, 0,0)
        cr.paint()

        w = self.allocation.width
        h = self.allocation.height
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgba(0.8,0.9,0.9,0.3)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(0.5*float(boss.opts.base))
        self.show_key_text(cr,w,h)

    def show_key_text(self,cr,w,h):
        font = pango.FontDescription(boss.opts.font)
        font.set_size(8*pango.SCALE)
        layout = cr.create_layout()
        layout.set_font_description(font)
        
        layout.set_markup("<b>%s</b>" % _('Teclado'))
        cr.move_to(40,15)
        cr.set_source_rgb(1,1,0.7)
        cr.show_layout(layout)
        layout.set_markup("") 

        cr.set_source_rgba(0.95,0.97,0.97,0.8)
        cr.rectangle(30,30,w-420,h-55)
        cr.fill_preserve()
        cr.set_source_rgb(0.35,0.6,0.3)
        cr.stroke()

        x = 30; y = 40
        ypos = 10; i = 0
        for t1,t2 in key_texts: 
            cr.set_source_rgb(0,0.4,0)
            layout.set_width(500*pango.SCALE)
            layout.set_text(t1)
            cr.move_to(x+10,y+i*18)
            cr.show_layout(layout)
            
            cr.set_source_rgb(0,0,0.4)
            layout.set_width(800*pango.SCALE)
            layout.set_text(t2)
            cr.move_to(x+100,y+i*18)
            cr.show_layout(layout)
            i += 1

        layout.set_markup("<b>%s</b>" % _('Raton'))
        cr.move_to(360,15)
        cr.set_source_rgb(1,1,0.7)
        cr.show_layout(layout)
        
        cr.set_source_rgba(0.95,0.97,0.97,0.8)
        cr.rectangle(350,30,w-378,h-55)
        cr.fill_preserve()
        cr.set_source_rgb(0.35,0.6,0.3)
        cr.stroke()
        
        x = 350; y = 40
        x1 = 445; x2 = 555
        cr.set_source_rgb(0,0,0.4)
        layout.set_markup("<b>%s</b>" % _('Accion'))
        cr.move_to(x1,y)
        cr.show_layout(layout)
        
        cr.set_source_rgb(0.4,0,0)
        layout.set_markup("<b>%s</b>" % _('Donde'))
        cr.move_to(x2,y)
        cr.show_layout(layout)
        layout.set_markup("") 

        x = 350; y = 60
        ypos = 10; i = 0
        for t1,t2,t3 in mouse_texts: 
            if t1:
                cr.set_source_rgb(0,0.4,0)
                layout.set_width(500*pango.SCALE)
                layout.set_text(t1)
                cr.move_to(x+10,y+i*18)
                cr.show_layout(layout)
            
            if t2:
                cr.set_source_rgb(0,0,0.4)
                layout.set_width(120*pango.SCALE)
                layout.set_text(t2)
                cr.move_to(x1,y+i*18)
                cr.show_layout(layout)
            
            if t3:
                cr.set_source_rgb(0.5,0,0)
                layout.set_width(800*pango.SCALE)
                layout.set_text(t3)
                cr.move_to(x2,y+i*18)
                cr.show_layout(layout)
            i += 1

key_texts = [ ('F1',_(': Esta ayuda')),
        ('Ctrl-Q',_(': Salir')),
        ('F11 (Esc)',_(': Pantalla completa')),
        ('Ctrl-G',_(': Exportar a imagen')),
        ('Ctrl-P',_(': Exportar a PDF - Imprimir')), 
        ('Ctrl-E',_(': Cuadro de entradas')),
        ('Ctrl-S',_(': Cuadro de configuracion')),
        ('Ctrl-F',_(': Buscar tecleando en listas')), 		
        ('Esc',_(': Cerrar ventana/dialogo')), 
        ('Ctrl-X',_(': Alternar casillas')), 
        ('Ctrl-C, F5',_(': Calendario')),  	
        ('Ctrl-A, F6',_(': PE')), 
        ('Ctrl-W',_(': Ventana auxiliar')), 		
        ('Ctrl-H',_(': Selector aspectos')), 
        ('Ctrl-D',_(': Diagramas')),
        ('Ctrl-Y',_(': Ciclos')), 
        ('Ctrl-R',_(': PE puente')), 
        ('Ctrl-L',_(': Localidades personalizadas')), 
        ('Ctrl-B',_(': Navegador rapido cartas')), 		
        (_('Cursores'),_(': Moverse en listas')), 
        (_('0-9 Tecl. num.'),_(': Seleccionar lista')),
        (_('+/- Tecl. num.'),_(': Rotar tambor')), 
        ('+/-',_(': Rotar casas (biografia)')) ] 

mouse_texts = [ 
        (_('Clic simple'),_('seleccionar pe'),_('pe, biografia')),
        ("",_('ojo'),_('personas recientes')),
        (_('Clic derecho'),_('menu secundario'),_('area de dibujo')),
        ("","",_('ventana auxiliar')),
        ("","",_('casillas')),
        ("","",_('listas de cartas')),
        (_('Doble clic'),_('restaurar fecha'),_('pe, biografia')),
        ("","",_('carta reloj, transitos')),
        ("","",_('selector de casas')),
        ("",_('principio de lista'),_('Vent.aux.')),
        (_('Arrastrar'),_('guia de grados'),_('area de dibujo')),
        ("",_('mover pe'),_('biografia')),
        ("",_('panorama'),_('acercar')),
        ("",_('mover registros'),_('entre tablas')),
        (_('Rueda'),_('rotar lista'),_('areas de dibujo')), 
        ("",_('rotar tambor'),_('casillas')),
        (_('Boton rueda'),_('principio lista'),_('lista principal')), 
        ("",_('ventana de grados'),_('principio lista principal')),
        ("",_('alternar posicion'),_('listas dobles/triples')),
        ("",_('alternar con guia'),_('acercar')),
        ("",_('mover pe ')+ u"180\u00b0",_('pe')),
        (_('   + Ctlr'),_('mover pe +')+u"30\u00b0",""),
        (_('   + Ctlr-May'),_('mover pe -')+u"30\u00b0","")
        ]

