#!/usr/bin/python
# -*- coding: utf-8 -*- 
import sys, os
import glob
import gettext
import atexit
import countries 
from config import read_config
lang_es = gettext.translation('astronex','./astronex/locale', languages=['es'])
lang_en = gettext.translation('astronex','./astronex/locale', languages=['en'])
lang_ca = gettext.translation('astronex','./astronex/locale', languages=['ca'])
lang_de = gettext.translation('astronex','./astronex/locale', languages=['de'])
langs = { 'en': lang_en, 'es': lang_es, 'ca': lang_ca, 'de': lang_de }

from extensions.path import path
version = "1.2"

def die(message):
    """Die in a command line way."""
    sys.exit(1)

try:
    import gtk
    import gobject
    if gtk.pygtk_version < (2, 8):
        die('Astro-Nex requires PyGTK >= 2.8. It only found %s.%s'
                % gtk.pygtk_version[:2])
except ImportError:
    die('Astro-Nex requires Python GTK bindings. They were not found.')


# Python 2.5
if sys.version_info < (2,5):
    die('Python 2.5 is required to run Astro-Nex. Only %s.%s was found.' %
            sys.version_info[:2])


home_dir = '.astronex'
config_file = 'cfg.ini'
default_db = 'charts.db'
ephe_path = 'ephe'
ephe_flag = 4

def check_home_dir(appath):
    """Set home dir, copying needed files"""
    global home_dir, ephe_flag
    default_home = path.joinpath(path.expanduser(path('~')), home_dir)
    
    if not path.exists(default_home):
        path.mkdir(default_home)
    ephepath = path.joinpath(default_home,ephe_path)
    if not path.exists(ephepath):
        path.mkdir(path.joinpath(default_home,ephe_path))
        path.copy(path.joinpath(appath,"astronex/resources/README"),ephepath)
    if ephepath.glob("*.se1"):
        ephe_flag = 2 
    if not path.exists(path.joinpath(default_home,default_db)):
        path.copy(path.joinpath(appath,"astronex/resources/charts.db"),default_home)

    home_dir = default_home
    

def init_config(homedir,opts,state): 
    ephepath = path.joinpath(homedir,opts.ephepath)
    from pysw import setpath
    setpath(str(ephepath))
    
    state.country = opts.country
    state.usa = {'false':False,'true':True}[opts.usa]
    state.database = opts.database
    state.setloc(opts.locality,opts.region)
    state.init_nowchart()
    state.curr_chart = state.now
    state.epheflag = ephe_flag
    opts.epheflag = ephe_flag

    if opts.favourites:
        try:
            tbl = opts.favourites
            nfav = int(opts.nfav)
            favs = state.datab.get_favlist(tbl,nfav,state.newchart())
            state.fav = favs
        except:
            pass
    
    from chart import orbs as ch_orbs
    orbs = [opts.lum,opts.normal,opts.short,opts.far,opts.useless]
    for l in orbs:
        state.orbs.append(map(float,l))
        ch_orbs.append(map(float,l)) 
    peorbs = [opts.pelum,opts.penormal,opts.peshort,opts.pefar,opts.peuseless]
    for l in peorbs:
        state.peorbs.append(map(float,l))
    for l in opts.transits:
        state.transits.append(float(l)) 
    opts.discard = [ int(x) for x in opts.discard ]

class Splash (gtk.Window):
    def __init__(self,appath):
        gtk.Window.__init__(self,gtk.WINDOW_POPUP)
        self.set_default_size(400, 250) 
        self.set_position (gtk.WIN_POS_CENTER)
        vbox = gtk.VBox()
        img = gtk.Image()
        splashimg = path.joinpath(appath,"astronex/resources/splash.png")
        img.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(splashimg))
        vbox.pack_start(img)
        self.add(vbox)

def init_ipshell():    
    ''' ipython suport (for linux)'''
    if sys.platform != 'win32': 
        try:
            __IPYTHON__
        except NameError:
            argv = ['']
            banner = exit_msg = ''
        else:
            argv = ['-pi1','In <\\#>:','-pi2','   .\\D.:','-po','Out<\\#>:']
            banner = '*** Nested interpreter ***'
            exit_msg = '*** Back in main IPython ***'

        #from IPython.Shell import IPShellEmbed
        #ipshell = IPShellEmbed(argv,banner=banner,exit_msg=exit_msg)
        #return ipshell 
        from IPython.config.loader import Config
        cfg = Config()
        cfg.InteractiveShellEmbed.prompt_in1="myprompt [\\#]> "
        cfg.InteractiveShellEmbed.prompt_out="myprompt [\\#]: "
        #cfg.InteractiveShellEmbed.profile=ipythonprofile 
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        shell = InteractiveShellEmbed(config=cfg, banner2=banner)
        shell.user_ns = {}
        return shell

class application(object):
    """The Nex Application."""

    def __init__(self,appath):
        self.home_dir = home_dir
        self.config_file = config_file
        self.default_db = default_db
        self.appath = appath
        self.version = version
        self.langs = langs

    def run(self):
        """Start Nex""" 
        splash = Splash(self.appath)
        splash.show_all()
        gobject.timeout_add(1000, splash.hide) # 5*1000 miliseconds
        gobject.idle_add(self.setup_app)
        gtk.main()

    def run_console(self):
        opts = read_config(self.home_dir)
        opts.home_dir = self.home_dir
        langs[opts.lang].install()
        countries.install(opts.lang)
        self.lang = opts.lang
        from state import Current
        from boss import Manager
        state = Current(self)
        init_config(self.home_dir,opts,state)
        boss = Manager(self,opts,state)
        boss.ipshell = init_ipshell() 
        boss.ipshell()

    def setup_app(self):
        opts = read_config(self.home_dir)
        opts.home_dir = self.home_dir
        langs[opts.lang].install()
        countries.install(opts.lang)
        self.lang = opts.lang
        from state import Current
        from boss import Manager
        state = Current(self)
        atexit.register(state.save_pool,self)
        init_config(self.home_dir,opts,state)
        boss = Manager(self,opts,state)
        from gui.winnex import WinNex
        mainwin = WinNex(boss)
        boss.set_mainwin(mainwin)
        #if 'DEBUG_NEX' in os.environ:
        #    boss.ipshell = init_ipshell() 
    
    def stop(self):
        """Stop Nex."""
        gtk.main_quit()

def main(appath,console=False):
    check_home_dir(appath)
    app = application(appath)
    if console:
        app.run_console()
    else:
        app.run()

