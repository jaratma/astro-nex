# -*- coding: utf-8 -*-

import os
import gtk, gobject
import cairo, pango
from StringIO import StringIO 
from configobj import ConfigObj, ConfigObjError
from .. extensions.path import path
from .. config import reload_config

boss = None

class IniEditor(gtk.Dialog):
    def __init__(self,parent):
        global boss
        boss = parent.boss
        gtk.Window.__init__(self)
        gtk.Dialog.__init__(self,
                _("Editor cfg.ini"), parent,
                gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CLOSE, gtk.RESPONSE_NONE,
                    gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        
        self.set_size_request(480,520)
        self.set_transient_for(parent)
        self.set_resizable(True)

        self.vbox.set_border_width(6)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textview.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse("#000")) 
        textbuffer = textview.get_buffer()
        sw.add(textview)
        self.vbox.pack_start(sw)

        cfgfile = path.joinpath(boss.opts.home_dir,'cfg.ini')
        infile = open(cfgfile, "r")

        if infile:
            self.cfgfile = cfgfile
            self.textbuffer = textbuffer
            string = infile.read()
            infile.close()
            textbuffer.set_text(string)


        self.connect("response", self.dlg_response)
        self.show_all()

    def dlg_response(self,dialog,rid):
        if rid == gtk.RESPONSE_OK:
            start = self.textbuffer.get_start_iter()
            end = self.textbuffer.get_end_iter()
            text = self.textbuffer.get_text(start,end)
            infile = StringIO(text)
            try:
                conf = ConfigObj(infile)
                conf.filename =  self.cfgfile
                conf.write()
                reload_config(conf,boss)
            except ConfigObjError, e:
                errdialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                        gtk.MESSAGE_ERROR,
                        gtk.BUTTONS_OK, e.message);
                result = errdialog.run()
                errdialog.destroy()
                line = int(e.message[22:-2])
                iter = self.textbuffer.get_iter_at_line_index(line,0)
                self.textbuffer.place_cursor(iter)
                return
        dialog.destroy()
        return
