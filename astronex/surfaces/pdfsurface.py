# -*- coding: utf-8 -*-
import os
import sys
import gtk
import cairo
import pango
import pangocairo
from .. drawing.dispatcher import DrawMixin
from .. gui.plagram_dlg import PgMixin
from .. drawing.datasheets import labels
from math import pi as PI
from .. utils import parsestrtime
from .. boss import boss
curr = boss.get_state()
opts = boss.opts

version = boss.get_version()
PDFH = 845.04685
PDFW = 597.50787 # A4 points
pdflabels = True

papers = {
        'A3': (845.04685,1195.0157),
        'A4': (597.50787,845.04685),
        'A5': (421.10079,597.50787),
        'custom': (597.50787,597.50787),
        'custom5': (421.10079,421.10079)
    }

singles = ['draw_nat', 'draw_nod', 'draw_house', 'draw_local',
        'draw_soul', 'draw_prof', 'draw_int', 'draw_single',
        'draw_radsoul']

suffixes = boss.suffixes

landscape = ['bio_nat','bio_nod','bio_soul','click_bridge','dyn_cuad','rad_and_transit','dyn_cuad2'] 
special = ['click_bridge','rad_and_transit'] 
clicks = ['click_hh','click_nn','click_hn','click_nh', 'dyn_cuad2',
'subject_click','click_bridge','click_rr','ascent_star','compo_one','compo_two','crown_comp',
'polar_star','wundersensi_star','paarwabe_plot','comp_pe','click_counterpanel'] 
couples = [ 'ascent_star','compo_one','compo_two','polar_star','wundersensi_star','paarwabe_plot','comp_pe','click_counterpanel'] 
roundedclicks = ['click_hh','click_nn','click_hn','click_nh', 'dyn_cuad2',
'subject_click','click_bridge','click_rr'] 
sheets = ['dat_nat','dat_house','dat_node',
                'prog_nat','prog_nod','prog_local','prog_soul']
class DrawPdf(object):
    w = PDFW

    @staticmethod
    def clicked(boss):
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
        name = DrawPdf.format_name()
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

        surface = DrawPdf.dispatch(filename)
        surface.finish() 
        
        if sys.platform == 'win32':
            os.startfile(filename) 
        else: 
            os.system("%s '%s' &" % (opts.pdfviewer,filename))

    @staticmethod
    def dispatch(filename,labels=True):
        w = PDFW
        h = PDFH
        if curr.opmode != 'simple' or curr.curr_op in landscape:
            w,h = h,w
        surface = cairo.PDFSurface(filename,w,h)
        surface.set_fallback_resolution(300,300)
        cr = pangocairo.CairoContext(cairo.Context(surface))
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(opts.base))
        dr = DrawMixin(opts,DrawPdf())
        if curr.opmode == 'double' or curr.curr_op in special:
            w *= 0.93
            cr.translate((PDFH - w)/2,0.0)
        elif curr.opmode == 'triple':
            h *= 0.95
            cr.translate(0.0,(PDFW - h)/2)
        elif curr.opmode == 'simple':
            if curr.curr_op.startswith('bio'):
                w *= 0.9
                h *= 0.9
                cr.translate((PDFH - w)/2,(PDFW - h)/2)
            elif curr.curr_op.startswith('dyn_c'):
                h *= 0.9
                w *= 0.8
                cr.translate((PDFH - w)/2,(PDFW-h)) 
            elif curr.curr_op == 'dyn_stars':
                h *= 0.7
                w *= 0.95
                cr.translate((PDFW - w)/2,(PDFH-h)/3) 
            elif curr.curr_op.startswith('subjec'):
                h *= 0.9 
                w *= 0.9
                cr.translate((PDFH - w)/10,0.0)
            elif curr.curr_op == 'click_counterpanel':
                h *= 0.75 
                cr.translate(0.0,(PDFH-h)/3)
            elif curr.curr_op in ['compo_one','compo_two']:
                h *= 0.9 
                cr.translate(0.0,(PDFH-h)/3)
            elif curr.curr_op == 'polar_star':
                h *= 0.8 
                w *= 0.9
                cr.translate((PDFW - w)/2,(PDFH-h)/3)
            else:
                h *= 0.9 
        DrawPdf.w = w
        DrawPdf.h = h 
        dr.dispatch_pres(cr,w,h)
        if curr.curr_op not in sheets and pdflabels:
            DrawPdf.d_pdf_labels(cr,w,h)
        elif curr.curr_op in ['dat_nat','dat_house','dat_node']: 
            DrawPdf.d_pdf_header(cr,w,h,sheet=True) 
        cr.show_page()
        return surface

    @staticmethod
    def simple_batch():
        w = PDFW
        h = PDFH
        name = curr.curr_chart.first.replace(' ','_')
        if sys.platform == 'win32':
            import winshell
            folder = winshell.my_documents()
        else: 
            folder = os.path.expanduser("~")
        filename = ".".join([name,'pdf'])
        filename = os.path.join(folder,filename)
        surface = cairo.PDFSurface(filename,w,h)
        surface.set_fallback_resolution(300,300)
        cr = pangocairo.CairoContext(cairo.Context(surface))
        cr.rectangle(0,0,w,h)
        cr.clip()
        cr.set_source_rgb(1.0,1.0,1.0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 
        cr.set_line_width(float(opts.base))
        dr = DrawMixin(opts,DrawPdf())
        h *= 0.9 
        DrawPdf.w = w
        DrawPdf.h = h 
        op = curr.curr_op
        for sop in singles:
            curr.curr_op = sop 
            dr.dispatch_pres(cr,w,h)
            if pdflabels:
                DrawPdf.d_pdf_labels(cr,w,h)
            cr.show_page()
        curr.curr_op = op 
        surface.finish()
    
    @staticmethod
    def pg_table_batch(table="plagram"):
        w = PDFH
        h = PDFW
        if sys.platform == 'win32':
            import winshell
            folder = winshell.my_documents()
        else: 
            folder = os.path.expanduser("~")
        curr.curr_op = "draw_planetogram"
        chlist = curr.datab.get_chartlist(table)
        chart = curr.curr_chart
        DrawPdf.shadow = True
        DrawPdf.personlines = False
        DrawPdf.turnpoints = True
        DrawPdf.crosspoints = True
        DrawPdf.useagecircle = False
        DrawPdf.extended = False
        class Da(object):
            class E(object): 
                def get_showAP(self): return False
            def __init__(self):
                self.drawer = Da.E()
        boss.da = Da()        
        
        for id, name,sur in chlist:
            wname = "_".join([name,sur,"pg"])
            filename = ".".join([wname,'pdf'])
            filename = os.path.join(folder,filename)
            surface = cairo.PDFSurface(filename,w,h)
            surface.set_fallback_resolution(300,300)
            cr = pangocairo.CairoContext(cairo.Context(surface))
            cr.set_source_rgb(1.0,1.0,1.0)
            cr.rectangle(0,0,w,h)
            cr.fill()
            cr.set_line_join(cairo.LINE_JOIN_ROUND) 
            cr.set_line_width(float(opts.base))
            dr = PgMixin(boss,DrawPdf())
            DrawPdf.w = w
            DrawPdf.h = h 
            curr.datab.load_chart(table,id,chart)
            dr.dispatch_simple(cr,w,h)
            cr.show_page()
            surface.finish()


    @staticmethod
    def format_name():
        if curr.opmode == 'simple':
            suffix = "".join([suffixes[curr.curr_op],'.pdf'])
        else:
            suffix = "".join([suffixes[curr.opleft][0],suffixes[curr.opright][0]])
            d_o_t = [2,3][curr.opmode == 'triple']
            suffix = "".join([suffix,str(d_o_t),'.pdf'])

        if curr.clickmode == 'click':
            names = [ n.replace(' ','_') for n in [curr.curr_chart.first,curr.curr_click.first]]
        else: 
            names = [curr.curr_chart.first.replace(' ','_')]
        names.append(suffix)
        name = "_".join(names)
        return name

    @staticmethod
    def d_pdf_header(cr,w,h,sheet=False):
        from datetime import datetime
        date = datetime.now().strftime("%d/%m/%Y")
        font = pango.FontDescription(opts.font)
        font.set_size(8*pango.SCALE)
        layout = cr.create_layout()
        layout.set_font_description(font)
        layout.set_text("Astro-Nex %s" % version)
        cr.set_source_rgb(0.2,0,0.9)
        if sheet:
            cr.move_to(50,h+20)
        else:
            cr.move_to(40,40)
        cr.show_layout(layout)
        layout.set_text(date)
        if sheet:
            cr.move_to(w-110,h+20)
        else:
            cr.move_to(w-90,40)
        cr.show_layout(layout)

    @staticmethod
    def d_pdf_labels(cr,w,h):
        font = pango.FontDescription(opts.font)
        font.set_size(8*pango.SCALE)
        cr.set_source_rgb(0.2,0,0.9)
        cr.identity_matrix()

        opmode = curr.opmode
        curr_op = curr.curr_op
        clickmode = curr.clickmode
        
        layout = cr.create_layout()
        layout.set_font_description(font)
        date,time = parsestrtime(curr.curr_chart.date)
        date = date + " " + time.split(" ")[0]
        geodat = curr.format_longitud() + " " + curr.format_latitud()
        name = curr.curr_chart.first + " " + curr.curr_chart.last
        if opmode == 'simple' and curr_op == 'draw_local':
            loc = curr.loc.city + " (" + t(curr.loc.country) + ")"
        else:
            loc = curr.curr_chart.city + " (" + t(curr.curr_chart.country) + ")"
        
        if opmode == 'simple'and (curr_op.startswith('bio') or curr_op.startswith('dyn_c')):
            glue = " "
        else:
            glue = "\n"

        if opmode != 'simple' or curr_op.startswith('dyn_c') or curr_op in clicks:
            label = ''
        else:
            label = labels[curr.curr_op] + glue
        
        if curr_op in couples:
            text = name
        else:
            text = label + name + glue + date + glue + loc + glue + geodat 
        layout.set_alignment(pango.ALIGN_CENTER)
        layout.set_text(text)
        ink,logical = layout.get_extents()
        xpos = logical[2]/pango.SCALE
        
        hfoot = 150
        if opmode == 'simple':
            if curr_op.startswith('bio'):
                w /= 0.9
                cr.move_to(w/2-xpos/2,40)
            elif curr_op.startswith('dyn_c'):
                h /= 0.9
                w /= 0.8
                if curr_op in clicks:
                    cr.move_to(w/2-xpos/2,40)
                    cr.show_layout(layout) 
                    d_second_label(cr,layout,label,glue,w/2,55)
                else:
                    cr.move_to(w/2-xpos/2,40)
            elif curr_op == 'dyn_stars':
                w /= 0.95
                h /= 0.7
                cr.move_to(w/2-xpos/2,h-hfoot)
            elif curr_op == 'rad_and_transit':
                w /= 0.93
                cr.move_to(w/2-xpos/2,h-130)
            elif curr_op in clicks:
                if curr_op.startswith('subjec'):
                    w /= 0.9
                    h /= 0.9
                elif curr_op == 'click_bridge':
                    w /= 0.93
                    h /= 0.9
                elif curr.curr_op == 'polar_star':
                    w /= 0.9 
                    h /= 0.8 
                else:
                    h /= 0.9
                if curr_op == 'click_counterpanel':
                    hfoot = -hfoot/3
                    cr.move_to(w/4-xpos/2,h-hfoot)
                elif curr_op in couples:
                    hfoot = hfoot/3
                    cr.move_to(w/4-xpos/2,h-hfoot)
                else:
                    cr.move_to(w/4-xpos/2,h-hfoot)
                cr.show_layout(layout)
                x = 3*w/4
                d_second_label(cr,layout,label,glue,x,h-hfoot)
            else:
                h /= 0.9
                cr.move_to(w/2-xpos/2,h-hfoot)
        elif opmode == 'double':
            hfoot = 100
            w /= 0.93
            if clickmode == 'click':
                cr.move_to(w/4-xpos/2,h-hfoot)
                cr.show_layout(layout)
                x = 3*w/4
                d_second_label(cr,layout,label,glue,x,h-hfoot)
            else:
                cr.move_to(w/2-xpos/2,h-hfoot)
        elif opmode == 'triple':
            h /= 0.95
            if clickmode == 'click':
                cr.move_to(w/5-xpos/2,h-450)
                cr.show_layout(layout)
                x = 4*w/5; y = h-450
                d_second_label(cr,layout,label,glue,x,y)
            else:
                cr.move_to(w/2-xpos/2,h-80)
        cr.show_layout(layout) 
        DrawPdf.d_pdf_header(cr,w,h)

def d_second_label(cr,layout,label,glue,x,y):
    date,time = parsestrtime(curr.curr_click.date)
    date = date + " " + time.split(" ")[0]
    geodat = curr.format_longitud() + " " + curr.format_latitud()
    name = curr.curr_click.first + " " + curr.curr_click.last
    loc = curr.curr_click.city + " (" + t(curr.curr_click.country) + ")"
    if curr.curr_op in couples:
        text = name
    else:
        text = label + name + glue + date + glue + loc + glue + geodat 
    layout.set_text(text)
    ink,logical = layout.get_extents()
    xpos = logical[2]/pango.SCALE
    cr.set_source_rgb(0.9,0,0.2)
    cr.move_to(x-xpos/2,y)
