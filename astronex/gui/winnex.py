# -*- coding: utf-8 -*-
import sys,os
from .. extensions.path import path
import gtk
from .. surfaces.layoutsurface import DrawMaster
from .. surfaces.pngsurface import DrawPng
from .. surfaces.pdfsurface import DrawPdf
#from .. surfaces import printsurface
from mainnb import MainPanel
from config_dlg import ConfigDlg
from customloc_dlg import CustomLocDlg
from chartbrowser import ChartBrowserWindow
from plagram_dlg import PlagramWindow
from entry_dlg import EntryDlg
from localsel import LocSelector
from aux_dlg import AuxWindow
from shell_dlg import ShellDialog
from quickhelp import HelpWindow
from inieditor import IniEditor

class WinNex(gtk.Window):

    def __init__(self,manager):
        gtk.Window.__init__(self)
        self.boss = manager
        appath = self.boss.app.appath
        appath = path.joinpath(appath,"astronex")
        self.entry = None
        self.locsel = None
        self.locselflag = False
        self.browser = None
        self.plagram = None
        self.set_title("Astro-Nex")
        self.connect('destroy', self.cb_exit)
        self.connect('key-press-event', self.on_key_press_event) 
        self.connect('configure-event', self.on_configure_event) 

        accel_group = gtk.AccelGroup()
        #accel_group.connect_group(ord('u'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.printpage_cb)
        accel_group.connect_group(ord('j'),gtk.gdk.CONTROL_MASK|gtk.gdk.SHIFT_MASK,gtk.ACCEL_LOCKED,self.swap_to_ten)
        accel_group.connect_group(ord('u'),gtk.gdk.CONTROL_MASK|gtk.gdk.SHIFT_MASK,gtk.ACCEL_LOCKED,self.swap_to_twelve)
        accel_group.connect_group(ord('e'),gtk.gdk.CONTROL_MASK|gtk.gdk.SHIFT_MASK,gtk.ACCEL_LOCKED,self.entry_calc)
        accel_group.connect_group(ord('n'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.locselector)
        accel_group.connect_group(ord('l'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.customloc_cb)
        accel_group.connect_group(ord('b'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.launch_chartbrowser)
        accel_group.connect_group(ord('w'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.launch_aux)
        accel_group.connect_group(ord('e'),gtk.gdk.MOD1_MASK,gtk.ACCEL_LOCKED,self.launch_plagram) 
        accel_group.connect_group(ord('r'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.launch_pebridge)
        accel_group.connect_group(ord('k'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.launch_shell)
        accel_group.connect_group(ord('i'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.launch_editor)
        accel_group.connect_group(ord('o'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.toggle_overlay)
        accel_group.connect_group(gtk.keysyms.F2,0,gtk.ACCEL_LOCKED,self.fake_modify_chart)
        accel_group.connect_group(gtk.keysyms.F3,0,gtk.ACCEL_LOCKED,self.fake_click_clock)
        accel_group.connect_group(ord('c'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.launch_calendar)
        accel_group.connect_group(gtk.keysyms.F4,0,gtk.ACCEL_LOCKED,self.launch_calendar)
        accel_group.connect_group(gtk.keysyms.F5,0,gtk.ACCEL_LOCKED,self.set_now)
        accel_group.connect_group(ord('a'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.show_pe)
        accel_group.connect_group(gtk.keysyms.F6,0,gtk.ACCEL_LOCKED,self.show_pe)
        accel_group.connect_group(ord('h'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.launch_selector)
        accel_group.connect_group(ord('y'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.launch_cycles)
        accel_group.connect_group(ord('d'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.show_diada)
        accel_group.connect_group(ord('x'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.swap_slot)
        accel_group.connect_group(ord('z'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.swap_storage)
        accel_group.connect_group(ord('u'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.load_couple)
        accel_group.connect_group(ord('1'),gtk.gdk.MOD1_MASK,gtk.ACCEL_LOCKED,self.load_one_fav)
        accel_group.connect_group(gtk.keysyms.plus,0,gtk.ACCEL_LOCKED,self.house_change)
        accel_group.connect_group(gtk.keysyms.minus,0,gtk.ACCEL_LOCKED,self.house_change)
        accel_group.connect_group(gtk.keysyms.Left,1,gtk.ACCEL_LOCKED,self.view_change)
        accel_group.connect_group(gtk.keysyms.Right,1,gtk.ACCEL_LOCKED,self.view_change)
        accel_group.connect_group(gtk.keysyms.Page_Up,gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.fake_scroll_up)
        accel_group.connect_group(gtk.keysyms.Page_Down,gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.fake_scroll_down)
        for i in range(0,10):
            ksym = getattr(gtk.keysyms,"KP_%s" % str(i))
            accel_group.connect_group(ksym,0,gtk.ACCEL_LOCKED,self.page_select)
            accel_group.connect_group(ksym,gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED,self.op_select)
        for i in ('Add','Subtract'):
            ksym = getattr(gtk.keysyms,"KP_%s" % str(i))
            accel_group.connect_group(ksym,0,gtk.ACCEL_LOCKED,self.scroll_pool )
        accel_group.connect_group(gtk.keysyms.Menu,0,gtk.ACCEL_LOCKED,self.popup_menu)
        self.add_accel_group(accel_group)

        hbox = gtk.HBox(False,3)
        self.add(hbox)
        
        ### toolbar
        self.tb = gtk.Toolbar()
        self.tb.set_size_request(300,-1)
        self.tb.set_tooltips(True)
        self.tb.set_style(gtk.TOOLBAR_ICONS)
        
        ti = gtk.ToolButton()
        ti.connect('clicked',self.cb_exit)
        img = gtk.Image()
        imgfile = path.joinpath(appath,"resources/gtk-quit-32.png")
        img.set_from_file(str(imgfile))
        ti.set_icon_widget(img)
        ti.add_accelerator('clicked',accel_group,ord('q'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED)
        ti.set_tooltip_text(_("Salir"))
        self.tb.insert(ti,0)
        
        #if 'DEBUG_NEX' in os.environ and sys.platform != 'win32': 
        #    tkon = gtk.ToolButton()
        #    img = gtk.Image()
        #    imgfile = os.path.join(appath,"resources/konsole-24.png")
        #    img.set_from_file(imgfile)
        #    tkon.set_icon_widget(img)
        #    tkon.connect('clicked',self.on_kon_clicked)
        #    tkon.set_tooltip_text(_("Terminal"))
        #    self.tb.insert(tkon,-1) 

        tfull = gtk.ToolButton()
        img = gtk.Image()
        imgfile = os.path.join(appath,"resources/fullscreen-32.png")
        img.set_from_file(imgfile)
        tfull.set_icon_widget(img)
        tfull.connect('clicked',self.on_fullscreen_clicked)
        tfull.toggled = True
        tfull.set_tooltip_text(_("Pantalla completa"))
        self.tb.insert(tfull,-1) 
        self.add_mnemonic(gtk.keysyms.F11,tfull)

        timg = gtk.ToolButton()
        img = gtk.Image()
        imgfile = os.path.join(appath,"resources/gnome-image-32.png")
        img.set_from_file(imgfile)
        timg.set_icon_widget(img)
        timg.connect('clicked',self.on_png_clicked)
        timg.add_accelerator('clicked',accel_group,ord('g'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED)
        timg.set_tooltip_text(_("Exportar a imagen"))
        self.tb.insert(timg,-1) 

        tpdf = gtk.ToolButton()
        img = gtk.Image()
        imgfile = os.path.join(appath,"resources/x-pdf-32.png")
        img.set_from_file(imgfile)
        tpdf.set_icon_widget(img)
        tpdf.connect('clicked',self.on_pdf_clicked)
        tpdf.add_accelerator('clicked',accel_group,ord('p'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED)
        tpdf.set_tooltip_text(_("Exportar a PDF/Imprimir"))
        self.tb.insert(tpdf,-1) 

        tentry = gtk.ToolButton()
        img = gtk.Image()
        imgfile = os.path.join(appath,"resources/gtk-compose-32.png")
        img.set_from_file(imgfile)
        tentry.set_icon_widget(img)
        tentry.connect('clicked',self.on_entry_clicked)
        tentry.add_accelerator('clicked',accel_group,ord('e'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED)
        tentry.set_tooltip_text(_("TEntradas"))
        self.tentry = tentry
        self.tb.insert(tentry,-1) 
        
        thelp = gtk.ToolButton()
        img = gtk.Image()
        imgfile = os.path.join(appath,"resources/gtk-properties-32.png")
        img.set_from_file(imgfile)
        thelp.set_icon_widget(img)
        thelp.connect('clicked',self.on_props_clicked)
        thelp.add_accelerator('clicked',accel_group,ord('s'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED)
        thelp.set_tooltip_text(_("TConfiguracion"))
        self.tb.insert(thelp,-1) 
        
        tabout = gtk.ToolButton()
        img = gtk.Image()
        imgfile = os.path.join(appath,"resources/stock_about.png")
        img.set_from_file(imgfile)
        tabout.set_icon_widget(img)
        tabout.connect('clicked',self.on_about_clicked,appath)
        tabout.set_tooltip_text(_("Acerca de Astro-Nex"))
        self.tb.insert(tabout,-1) 

        self.mpanel = MainPanel(self.boss)

        vbox = gtk.VBox()
        vbox.pack_start(self.tb,False,False)
        vbox.pack_start(self.mpanel,True,True)

        hbox.pack_start(vbox,False,False)
        self.da = DrawMaster(self.boss)
        scr_width = gtk.gdk.screen_width()
        scr_height = gtk.gdk.screen_height()
        if scr_width >= 1280:
            self.da.set_size_request(660,660)
        else:
            self.da.set_size_request(500,500)

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add_with_viewport(self.da)
        scrolled.set_shadow_type(gtk.SHADOW_NONE)
        hbox.pack_start(scrolled)
        self.da.ha = scrolled.get_hadjustment()
        self.da.va = scrolled.get_vadjustment()

        imgfile = path.joinpath(appath,"resources/iconex-22.png")
        self.set_icon_from_file(str(imgfile))
        scr_width = gtk.gdk.screen_width()
        scr_height = gtk.gdk.screen_height()
        #if scr_width >= 1280:
        #    scr_width *= 0.9
        #if scr_height >= 768:
        #    scr_height *= 0.79
        self.set_default_size(int(scr_width), int(scr_height))
        self.scr_width = scr_width
        self.show_all()
        wpos = self.window.get_position()
        self.pos_x = wpos[0]
        self.pos_y = wpos[1]

    def on_configure_event(self,widget,event):
        self.pos_x = event.x
        self.pos_y = event.y

    def on_key_press_event(self,window,event): 
        if event.keyval == gtk.keysyms.F11 or (event.keyval == gtk.keysyms.Escape and self.da.__class__.fullscreen): 
            self.tb.get_nth_item(1).emit('clicked')
        elif event.keyval == gtk.keysyms.F1:
            self.show_help()
        return False
    
    def activate_entry(self):
        self.tentry.emit('clicked')
    
    def cb_exit(self,e):
        gtk.main_quit()

    def on_pdf_clicked(self,but):
        DrawPdf.clicked(self.boss)
    
    def on_png_clicked(self,but):
        DrawPng.clicked(self.boss)
    
    def on_props_clicked(self,but):
        ConfigDlg(self)
    
    def on_entry_clicked(self,but):
        if not self.entry:
            self.entry = EntryDlg(self) 

    def entry_calc(self,a,b,c,d):
        if not self.entry:
            self.entry = EntryDlg(self) 
            self.entry.modify_entries(self.boss.state.calc)
    
    def locselector(self,a,b,c,d):
        self.locselflag = True
        if not self.locsel:
            self.locsel = LocSelector(self) 
    
    def on_fullscreen_clicked(self,full):
        if full.toggled:
            full.toggled = False
            self.mpanel.hide()
            self.tb.hide()
            self.boss.set_fullscreen_state(True)
            self.fullscreen()
        else:
            full.toggled = True
            self.tb.show()
            self.mpanel.show()
            self.boss.set_fullscreen_state(False) 
            self.unfullscreen()

    def on_kon_clicked(self,but):
        self.boss.ipshell()

    def on_about_clicked(self,but,appath):
        about = gtk.AboutDialog()
        about.connect("response", self.on_about_response)
        about.connect("close", self.on_about_close)
        #about.connect("delete_event", self.on_about_close)
        about.set_name("Astro-Nex")
        about.set_version(self.boss.app.version)
        about.set_comments(unicode(_("Programa de calculo y dibujo de cartas astrologicas segun el metodo API"), "utf-8"))
        file = path.joinpath(appath,"resources/COPYING")
        about.set_license(open(file).read())
        about.set_copyright(unicode("Copyright © 2006","utf-8"))
        about.set_website("http://astro-nex.com")
        about.set_authors([unicode("Jose Antonio Rodríguez <jar@eideia.net>","utf-8")])
        imgfile = path.joinpath(appath,"resources/splash.png")
        logo = gtk.gdk.pixbuf_new_from_file(imgfile)
        about.set_logo(logo)
        about.show_all()

    def on_about_response(self,dialog,response):
        if response < 0:
            dialog.destroy()
            dialog.emit_stop_by_name('response')
    
    def on_about_close(self,widget,event=None):
        widget.destroy()
        return True

    #def printpage_cb(self,acgroup,actable,keyval,mod):
    #    printsurface.printpage(self.boss)
    
    def customloc_cb(self,acgroup,actable,keyval,mod):
        CustomLocDlg(self.boss)
    
    def launch_chartbrowser(self,acgroup,actable,keyval,mod):
        if not self.browser:
            self.browser = ChartBrowserWindow(self)
    
    def launch_chartbrowser_from_mpanel(self):
        if not self.browser:
            self.browser = ChartBrowserWindow(self)
    
    def launch_plagram(self,acgroup,actable,keyval,mod):
        if not self.plagram:
            self.plagram = PlagramWindow(self)

    def launch_aux(self,acgroup,actable,keyval,mod):
        self.da.auxwins.append(AuxWindow(self))
    
    def launch_aux_from_browser(self,chart):
        self.da.auxwins.append(AuxWindow(self,chart=chart))
    
    def launch_pebridge(self,acgroup,actable,keyval,mod):
        item = self.mpanel.toolbar.get_nth_item(6)
        item.set_active(not item.get_active())
    
    def launch_shell(self,acgroup,actable,keyval,mod):
        ShellDialog(self.boss)
    
    def launch_editor(self,acgroup,actable,keyval,mod):
        IniEditor(self)
    
    def launch_calendar(self,acgroup,actable,keyval,mod):
        item = self.mpanel.toolbar.get_nth_item(0)
        item.set_active(not item.get_active())

    def show_pe(self,acgroup,actable,keyval,mod):
        item = self.mpanel.toolbar.get_nth_item(1)
        item.set_active(not item.get_active())

    def launch_selector(self,acgroup,actable,keyval,mod):
        item = self.mpanel.toolbar.get_nth_item(3)
        item.set_active(not item.get_active())

    def launch_cycles(self,acgroup,actable,keyval,mod):
        item = self.mpanel.toolbar.get_nth_item(4)
        item.set_active(not item.get_active())

    def show_diada(self,acgroup,actable,keyval,mod):
        item = self.mpanel.toolbar.get_nth_item(5)
        item.set_active(not item.get_active())

    def swap_slot(self,acgroup,actable,keyval,mod):
        self.mpanel.slot_act_inactive()
    
    def swap_storage(self,acgroup,actable,keyval,mod):
        self.mpanel.swap_storage() 

    def load_one_fav(self,acgroup,actable,keyval,mod):
        self.boss.load_one_fav()
    
    def load_couple(self,acgroup,actable,keyval,mod):
        self.boss.load_couple()
    
    def show_help(self):
        HelpWindow(self)
        
    def swap_to_ten(self,acgroup,actable,keyval,mod):
        self.boss.da.drawer.aspmanager.swap_to_ten()
        self.boss.da.redraw()

    def swap_to_twelve(self,acgroup,actable,keyval,mod):
        self.boss.da.drawer.aspmanager.swap_to_twelve()
        self.boss.da.redraw()
    
    def page_select(self,acgroup,actable,keyval,mod):
        s = gtk.keysyms
        kcodes = {s.KP_0:'transit', s.KP_1:'charts', s.KP_2:'clicks', s.KP_3:'bio', s.KP_4:'double1',
                s.KP_5:'triple1', s.KP_6:'data', s.KP_7:'diagram', s.KP_8:'double2', s.KP_9:'triple2' }
        thisname = kcodes[keyval]
        for but in self.mpanel.chooser.groups_table.get_children():
            if but.get_data('name') == thisname:
                but.set_active(True)
                break

    def op_select(self,acgroup,actable,keyval,mod):
        s = gtk.keysyms
        kcodes = [s.KP_0,s.KP_1,s.KP_2, s.KP_3, s.KP_4,
                s.KP_5, s.KP_6, s.KP_7, s.KP_8, s.KP_9]
        n = kcodes.index(keyval)
        nb = self.boss.mpanel.chooser.notebook
        v = nb.get_nth_page(nb.get_current_page())
        v.get_selection().select_path(n % len(v.get_model()),)

    def scroll_pool(self,acgroup,actable,keyval,mod):
        if  keyval == gtk.keysyms.KP_Add:
            delta = 1
        elif keyval == gtk.keysyms.KP_Subtract:
            delta = -1
        self.mpanel.scroll_pool(delta)

    def house_change(self,acgroup,actable,keyval,mod):
        if self.da.hselvisible:
            if  keyval == gtk.keysyms.plus:
                self.da.hsel.child.house_updown(1)
            else:
                self.da.hsel.child.house_updown(-1)

    def view_change(self,acgroup,actable,keyval,mod):
        nb = self.boss.mpanel.chooser.notebook
        page = nb.get_current_page()
        if page < 6:
            return
        if  keyval == gtk.keysyms.Right:
            val = 2
        elif  keyval == gtk.keysyms.Left:
            val = -2
        page = nb.get_nth_page(page)
        views = page.get_children()
        n = len(views)
        for v in range(n):
            if views[v].props.has_focus:
                views[(v+val)%(n+1)].grab_focus()
                break

    def popup_menu(self,acgroup,actable,keyval,mod):
        self.da.popup_menu()

    def fake_scroll_up(self,acgroup,actable,keyval,mod):
        event = gtk.gdk.Event(gtk.gdk.SCROLL)
        event.direction = gtk.gdk.SCROLL_UP
        self.da.on_scroll(self.da,event)
    
    def fake_scroll_down(self,acgroup,actable,keyval,mod):
        event = gtk.gdk.Event(gtk.gdk.SCROLL)
        event.direction = gtk.gdk.SCROLL_DOWN
        self.da.on_scroll(self.da,event)

    def set_now(self,acgroup,actable,keyval,mod):
        self.da.panel.nowbut.emit('clicked')

    def fake_click_clock(self,acgroup,actable,keyval,mod):
        slot = self.mpanel.pool[self.mpanel.active_slot]
        slot.clock.emit('clicked')

    def fake_modify_chart(self,acgroup,actable,keyval,mod):
        slot = self.mpanel.pool[self.mpanel.active_slot]
        slot.mod.emit('clicked')

    def toggle_overlay(self,acgroup,actable,keyval,mod):
        self.da.toggle_overlay()

