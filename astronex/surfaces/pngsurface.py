# -*- coding: utf-8 -*-
import os
import sys
import gtk
import cairo
import pangocairo
import pango
import PIL.Image
import PIL.ImageOps
from .. drawing.dispatcher import DrawMixin
from .. utils import parsestrtime
from .. boss import boss
curr = boss.get_state()
opts = None
minim = None
MAGICK_SCALE = 0.002

suffixes = boss.suffixes

class ImageExportDialog(gtk.Dialog):
    '''Save image config dialog'''

    def __init__(self,pg=False):
        gtk.Dialog.__init__(self,
                _("Exportar como imagen"), None,
                gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                    gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        self.vbox.set_border_width(3)
        self.vbox.set_spacing(6)
        
        self.vbox.pack_start(self.make_control(),False,False)
        self.vbox.pack_start(gtk.HSeparator(),True,True)
        chooser = gtk.FileChooserWidget(action=gtk.FILE_CHOOSER_ACTION_SAVE)
        self.vbox.pack_start(chooser,False,False)
        self.chooser = chooser
        self.chooser.set_size_request(600,400)
        
        
        self.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        #filter.add_mime_type("image/tiff")
        filter.set_name(_("Imagen"))
        self.chooser.add_filter(filter)
        
        if pg:
            name = curr.curr_chart.first + "_" + curr.curr_chart.last + "_pg"
        else:
            name = curr.curr_chart.first + "_" + suffixes[curr.curr_op]

        ext =  self.typefile_chooser.get_active_text()
        self.chooser.set_current_name(name+"."+ext)
        if sys.platform == 'win32':
            import winshell
            self.chooser.set_current_folder(winshell.my_documents())
        else: 
            self.chooser.set_current_folder(os.path.expanduser("~"))
        self.chooser.set_do_overwrite_confirmation(True)
        self.show_all()

    def make_control(self):
        tab = gtk.Table(2,3)
        tab.set_row_spacings(6)
        tab.set_col_spacings(12)
        tab.set_homogeneous(False)
        tab.set_border_width(6)
        
        #left
        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_EDGE) 
        label = gtk.Label(_("Anchura"))
        buttbox.pack_start(label)
        adj = gtk.Adjustment(int(boss.opts.hsize), 1, 10000, 1, 1, 1)
        hdim  = gtk.SpinButton(adj)
        hdim.set_alignment(1.0)
        hdim.set_numeric(True)
        lbl = 'hsize'
        adj.connect('value-changed', self.spin_imgsize,hdim,lbl)
        hdim.connect('changed', self.entry_imgsize,lbl)
        buttbox.pack_start(hdim)
        tab.attach(buttbox,0,1,0,1)
        
        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_EDGE) 
        label = gtk.Label(_("Altura"))
        buttbox.pack_start(label)
        adj = gtk.Adjustment(int(boss.opts.vsize), 1, 10000, 1, 1, 1)
        vdim  = gtk.SpinButton(adj)
        vdim.set_alignment(1.0)
        vdim.set_numeric(True)
        lbl = 'vsize'
        adj.connect('value-changed', self.spin_imgsize,vdim,lbl)
        vdim.connect('changed', self.entry_imgsize,lbl)
        buttbox.pack_start(vdim) 
        tab.attach(buttbox,0,1,1,2)
        
        #right
        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_EDGE) 
        label = gtk.Label(_("Resolucion"))
        buttbox.pack_start(label)
        adj = gtk.Adjustment(int(boss.opts.resolution), 1, 600, 1, 1, 1)
        res  = gtk.SpinButton(adj)
        res.set_alignment(1.0)
        res.set_numeric(True)
        adj.connect('value-changed', self.spin_change_res,res)
        res.connect('changed', self.entry_change_res)
        buttbox.pack_start(res)
        tab.attach(buttbox,1,2,0,1)
    
        buttbox = gtk.HButtonBox()
        buttbox.set_layout(gtk.BUTTONBOX_EDGE) 
        label = gtk.Label(_("Tipo"))
        buttbox.pack_start(label)
        store = gtk.ListStore(str)
        store.append([_('png')])
        store.append([_('jpg')])
        #store.append([_('tiff')])
        combo = gtk.ComboBox(store)
        cell = gtk.CellRendererText()
        combo.pack_start(cell,True)
        combo.add_attribute(cell,'text',0)
        combo.set_active(0)
        combo.connect("changed",self.typefile_changed)
        self.typefile_chooser = combo
        buttbox.pack_start(combo)
        tab.attach(buttbox,1,2,1,2)
        return tab
    
    def typefile_changed(self,combo):
        ext = combo.get_active_text()
        base = os.path.basename(self.chooser.get_filename())
        root,oldext = os.path.splitext(base)
        self.chooser.set_current_name(root+"."+ext)

    def spin_imgsize(self,adj,spin,lbl):
        opt = spin.get_value_as_int() 
        setattr(boss.opts,lbl,opt)

    def entry_imgsize(self,spin,lbl):
        try:
            opt = int(spin.get_text())
        except ValueError:
            return
        setattr(boss.opts,lbl,opt)

    def spin_change_res(self,adj,spin):
        opt = spin.get_value_as_int() 
        boss.opts.resolution = opt
    
    def entry_change_res(self,spin):
        try:
            opt = int(spin.get_text())
        except ValueError:
            return
        boss.opts.resolution = opt

class DrawPng(object):
    @staticmethod
    def clicked(boss):
        global opts,minim
        opts = boss.opts

        dialog = ImageExportDialog()

        filename = None
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename = dialog.chooser.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()

        if filename is None or filename == '': return

        w = int(opts.hsize)
        h = int(opts.vsize)
        if curr.curr_op in ['compo_one','compo_two']:
            w = 800
            h = 1100
        minim = min(w,h)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        cr = pangocairo.CairoContext(cairo.Context(surface))
        cr.set_source_rgba(1.0,1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(opts.base))
        dr = DrawMixin(opts,DrawPng())
        dr.dispatch_pres(cr,w,h)
        if opts.labels == 'true' or curr.curr_op in ['compo_one','compo_tow']:
            draw_label(cr,w,h)
        
        s = surface
        d = s.get_data()
        for i in xrange(0,len(d),4):
            d[i],d[i+2] = d[i+2],d[i]
        
        im = PIL.Image.frombuffer("RGBA", (s.get_width(),s.get_height()),d,"raw","RGBA",0,1)
        res = int(opts.resolution)
        im.info['dpi'] = (res,res)
        im.save(filename, dpi=im.info['dpi'])
        #surface.write_to_png(filename) 

        if sys.platform == 'win32':
            os.startfile(filename) 
        else: 
            os.system("%s '%s' &" % (opts.pngviewer,filename))

    @staticmethod
    def simple_batch(table="plagram"):
        global opts
        opts = boss.opts
        w = 1280 
        h = 1020
        if sys.platform == 'win32':
            import winshell
            folder = winshell.my_documents()
        else: 
            folder = os.path.expanduser("~")
        curr.curr_op = "draw_planetogram"
        chlist = curr.datab.get_chartlist(table)
        chart = curr.curr_chart
        
        for id, name,sur in chlist:
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
            cr = pangocairo.CairoContext(cairo.Context(surface))
            cr.set_source_rgb(1.0,1.0,1.0)
            cr.rectangle(0,0,w,h)
            cr.fill()
            cr.set_line_join(cairo.LINE_JOIN_ROUND) 
            cr.set_line_width(float(opts.base))
            dr = DrawMixin(opts,DrawPng())
            curr.datab.load_chart(table,id,chart)
            dr.dispatch_pres(cr,w,h)
            wname = "_".join([name,sur,"pg"])
            filename = ".".join([wname,'png'])
            filename = os.path.join(folder,filename)
            #d_name(cr,w,h)
            surface.write_to_png(filename) 

#im.save("itest.jpg", dpi=im.info['dpi'])
#im.save("itest.tiff", dpi=im.info['dpi'])


def draw_label(cr,w,h): 
    cr.identity_matrix() 
    clickops = ['click_hh','click_nn','click_bridge','click_nh','click_rr',
            'click_ss','click_rs','click_sn','ascent_star','wundersensi_star',
            'polar_star','paarwabe_plot','crown_comp',
            'dyn_cuad2','click_hn','subject_click'] 
    sheetopts = ['dat_nat', 'dat_nod', 'dat_house', 'prog_nat', 'prog_nod', 
            'prog_local', 'prog_soul' ]

    if curr.curr_op in clickops or (curr.clickmode == 'click' and curr.opmode != 'simple'): 
        d_name(cr,w,h,kind='click')
    elif curr.curr_op in ['compo_one','compo_two']:
        compo_name(cr,w,h)
    elif curr.curr_op not in sheetopts:
        d_name(cr,w,h)

def compo_name(cr,w,h):
    layout = cr.create_layout()
    font = pango.FontDescription(opts.font)
    font.set_size(int(7*pango.SCALE*minim*0.9*MAGICK_SCALE))
    layout.set_font_description(font)
    h *= 0.995
    mastcol = (0.8,0,0.1)
    clickcol = (0,0,0.4)    
    mastname = "%s %s" % (curr.curr_chart.first,curr.curr_chart.last)
    clickname = "%s %s" % (curr.curr_click.first,curr.curr_click.last)
    cr.set_source_rgb(*mastcol)
    layout.set_alignment(pango.ALIGN_RIGHT) 
    layout.set_text(clickname)
    ink,logical = layout.get_extents()
    xpos = logical[2]/pango.SCALE
    ypos = logical[3]/pango.SCALE
    cr.move_to(w-xpos-30,h-ypos)
    cr.show_layout(layout)
    cr.set_source_rgb(*clickcol)
    layout.set_alignment(pango.ALIGN_LEFT) 
    layout.set_text(mastname) 
    ypos = logical[3]/pango.SCALE
    cr.move_to(30,h-ypos)
    cr.show_layout(layout)

def d_name(cr,w,h,kind='radix'):
    layout = cr.create_layout()
    font = pango.FontDescription(opts.font)
    font.set_size(int(6*pango.SCALE*minim*MAGICK_SCALE))
    layout.set_font_description(font)
    h *= 0.995
    
    mastcol = (0,0,0.4)
    clickcol = (0.8,0,0.1)
    mastname = "%s %s" % (curr.curr_chart.first,curr.curr_chart.last)
    clickname = "%s %s" % (curr.curr_click.first,curr.curr_click.last)
    
    if kind == "click":
        mastcol, clickcol = clickcol, mastcol
        mastname, clickname = clickname, mastname
        date,time = parsestrtime(curr.curr_click.date)
        date = date + " " + time.split(" ")[0]
        geodat = curr.format_longitud(kind='click') + " " + curr.format_latitud(kind='click')
        loc = curr.curr_click.city + " (" + t(curr.curr_chart.country)[0] + ") "
        text = "\n" + date + "\n"  + loc + geodat
    else:
        date,time = parsestrtime(curr.curr_chart.date)
        date = date + " " + time.split(" ")[0]
        geodat = curr.format_longitud() + " " + curr.format_latitud()
        loc = curr.curr_chart.city + " (" + t(curr.curr_chart.country)[0] + ") "
        text = "\n" + date + "\n"  + loc + geodat

    cr.set_source_rgb(*mastcol)
    
    layout.set_alignment(pango.ALIGN_RIGHT) 
    layout.set_text(mastname+text)
    ink,logical = layout.get_extents()
    xpos = logical[2]/pango.SCALE
    ypos = logical[3]/pango.SCALE
    cr.move_to(w-xpos-5,h-ypos)
    cr.show_layout(layout)

    if kind == 'click':
        cr.set_source_rgb(*clickcol)
        layout.set_alignment(pango.ALIGN_LEFT) 
        date,time = parsestrtime(curr.curr_chart.date)
        date = date + " " + time.split(" ")[0]
        geodat = curr.format_longitud() + " " + curr.format_latitud()
        loc = curr.curr_chart.city + " (" + t(curr.curr_chart.country)[0] + ") "
        text = "\n" + date + "\n"  + loc + geodat
        layout.set_text(clickname+text)
        
        ypos = logical[3]/pango.SCALE
        cr.move_to(0+5,h-ypos)
        cr.show_layout(layout)
