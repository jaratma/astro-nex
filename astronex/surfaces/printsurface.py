# -*- coding: utf-8 -*-
import os
import sys
import gtk
import cairo
import pango
import pangocairo
from .. drawing.dispatcher import DrawMixin
from .. drawing.datasheets import labels
from .. boss import boss
curr = boss.get_state()
opts = boss.opts

version = boss.get_version()
PDFH = 845.04685*0.9

def draw_page(op,context,npages,boss):
    cr = context.get_cairo_context()

    w = 597.50787 # A4 points
    h = 845.04685

    if curr.opmode == 'double':
        w,h = h,w
    dr = DrawMixin(opts)
    
    if curr.opmode != 'simple':
        dr.dispatch_pres(cr,w,h)
    else:
        getattr(dr,curr.curr_op)(cr,w,h)

def printpage(boss):
    filename = "test.pdf"
    print_ = gtk.PrintOperation()
    print_.set_unit(gtk.UNIT_POINTS)
    print_.set_n_pages(1)
    print_.set_export_filename(filename)

    print_.connect('draw_page', draw_page,boss)
    res = print_.run(gtk.PRINT_OPERATION_ACTION_PRINT)
    return

