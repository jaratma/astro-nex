# -*- coding: utf-8 -*-
import sys,os
import gtk
import datetime
import re
import astronex.state as state
from .. utils import degtodec
curr = None

mstar_bugloc = { 'Jaen': u'Jaén', 
        'Almeria': u'Almería', 
        'Avila': u'Ávila',
        'Cadiz': u'Cádiz',
        'Caceres': u'Cáceres',
        'Cordoba': u'Córdoba',
        'Leon': u'León',
        'Malaga': u'Málaga',
        'L Palmas de Gran Canaria': u'Las Palmas de Gran Canaria' }

ccodes = {
'AFG':u'AF'	,	#Afganistán
'ARM':u'AM'	,	#Armenia
'ASB':u'AJ'	,	#Azerbaiján
'BRN':u'BA'	,	#Bahrain
'BD' :u'BG'  ,	#Bangla Desh
'BHU':u'BT'	,	#Bhután
'BRU':u'BX'	,	#Brunei
'K'  :u'CB'  ,	#Camboya
'TJ' :u'CH'  ,	#China
'CY' :u'CY'  ,	#Chipre
'GRG':u'GG'	,	#Georgia
'HKG':u'HK'	,	#Hong Kong
'IND':u'IN'	,	#India
'RI' :u'ID'  ,	#Indonesia
'IR' :u'IR'  ,	#Irán
'IRQ':u'IZ'	,	#Irak
'IL' :u'IS'  ,	#Israel
'J'  :u'JA'  ,	#Japón
'JOR':u'JO'	,	#Jordania
'KAZ':u'KZ'	,	#Kazajstán
'KOR':u'KN'	,	#Corea del Norte
'ROK':u'KS'	,	#Corea del Sur
'KWT':u'KU'	,	#Kuwait
'KIR':u'KG'	,	#Kirguizistán
'LAO':u'LA'	,	#Laos
'RL' :u'LE'  ,	#Líbano
'MAL':u'MY'	,	#Malasia
'MDV':u'MV'	,	#Maldivas
'MOG':u'MG'	,	#Mongolia
'MYA':u'BM'	,	#Myanmar (Birmania)
'NEP':u'NP'	,	#Nepal
'OMN':u'MU'	,	#Omán
'PAK':u'PK'	,	#Pakistán
'RP' :u'RP'  ,	#Filipinas
'Q'  :u'QA'  ,	#Qatar
'SA' :u'SA'  ,	#Arabia Saudita
'SGP':u'SN'	,	#Singapur
'CL' :u'CE'  ,	#Sri Lanka
'SYR':u'SY'	,	#Siria
'RC' :u'TW'  ,	#Taiwán
'TAJ':u'TI'	,	#Tadschikistan
'THA':u'TH'	,	#Tailandia
'TR' :u'TU'  ,	#Turquía
'TUR':u'TX'	,	#Turkmenistan
'UAE':u'AE'	,	#Emiratos Arabes
'UZB':u'UZ'	,	#Uzbekistan
'VN' :u'VM'  ,	#Vietnam
'YMD':u'YM'	,	#Yemen
'DZ' :u'AG'  ,	#Argelia
'ANG':u'AO'	,	#Angola
'RPH':u'BN'	,	#Benin
'RB' :u'BC'  ,	#Botswana
'BF' :u'UV'  ,	#Burkina Faso
'BU' :u'BY'  ,	#Burundi
'CAM':u'CM'	,	#Camerun
'KVR':u'CV'	,	#Cabo Verde
'RCA':u'CT'	,	#Central-Africa
'CHA':u'CD'	,	#Chad
'KOM':u'CN'	,	#Comoros
'RCB':u'CF'	,	#Congo (Brazzaville)
'ZR' :u'CG'  ,	#Congo (Kinshasa)
'DH' :u'DJ'  ,	#Djibouti
'ET' :u'EG'  ,	#Egipto
'AQG':u'EK'	,	#Guinea ecuatorial
'ETH':u'ET'	,	#Etiopía
'GAB':u'GB'	,	#Gabón
'GAM':u'GA'	,	#Gambia
'GH' :u'GH'  ,	#Ghana
'GUI':u'GV'	,	#Guinea
'GBA':u'PU'	,	#Guinea-Bissau
'CI' :u'IV'  ,	#Costa de Marfil
'EAK':u'KE'	,	#Kenya
'LS' :u'LT'  ,	#Lesotho
'LB' :u'LI'  ,	#Liberia
'LAR':u'LY'	,	#Libia
'RM' :u'MA'  ,	#Madagascar
'MW' :u'MI'  ,	#Malawi
'RMM':u'ML'	,	#Mali
'RIM':u'MR'	,	#Mauritania
'MS' :u'MP'  ,	#Mauricio
'MY' :u'MF'  ,	#Mayotte
'MA' :u'MO'  ,	#Marruecos
'MOZ':u'MZ'	,	#Mozambique
'NAB':u'WA'	,	#Namibia
'RN' :u'NG'  ,	#Níger
'WAN':u'NI'	,	#Nigeria
'REU':u'RE'	,	#Reunión
'RWA':u'RW'	,	#Ruanda
'SHA':u'SH'	,	#Santa Helena
'STP':u'TP'	,	#Santo Tomé & Príncipe
'SN' :u'SG'  ,	#Senegal
'SY' :u'SE'  ,	#Seychelles
'WAL':u'SL'	,	#Sierra Leona
'SP' :u'SO'  ,	#Somalia
'ZA' :u'SF'  ,	#Sudáfrica
'FS' :u'SU'  ,	#Sudán
'SD' :u'WZ'  ,	#Swazilandia
'EAT':u'TZ'	,	#Tanzania
'TG' :u'TO'  ,	#Togo
'TN' :u'TS'  ,	#Túnez
'EAV':u'UG'	,	#Uganda
'Z'  :u'ZA'  ,	#Zambia
'ZW' :u'ZI'  ,	#Zimbabwe
'ANT':u'AC'	,	#Antigua & Barbuda
'RA' :u'AR'  ,	#Argentina
'AGU':u'AV'	,	#Anguilla
'BDS':u'BB'	,	#Barbados
'BPA':u'BD'	,	#Bermudas
'BS' :u'BF'  ,	#Bahamas
'BH' :u'BH'  ,	#Belice
'BOL':u'BL'	,	#Bolivia
'BR' :u'BR'  ,	#Brasil
'CDN':u'CA'	,	#Canadá
'RCH':u'CI'	,	#Chile
'CAY':u'CJ'	,	#Islas Caimán
'CO' :u'CO'  ,	#Colombia
'CR' :u'CS'  ,	#Costa Rica
'C'  :u'CU'  ,	#Cuba
'WD' :u'DO'  ,	#Dominica
'DOM':u'DR'	,	#República Dominicana
'EC' :u'EC'  ,	#Ecuador
'ES' :u'ES'  ,	#El Salvador
'FGU':u'FG'	,	#Guayana Fr.
'FGB':u'FK'	,	#Islas Malvinas
'WG' :u'GJ'  ,	#Granada
'GRO':u'GL'	,	#Groenlandia
'GKA':u'GP'	,	#Guadalupe
'GCA':u'GT'	,	#Guatemala
'GUY':u'GY'	,	#Guyana
'RH' :u'HA'  ,	#Haití
'HON':u'HO'	,	#Honduras
'JA' :u'JM'  ,	#Jamaica
'MQU':u'MB'	,	#Martinique
'MTT':u'MH'	,	#Montserrat
'MEX':u'MX'	,	#México
'SME':u'NS'	,	#Suriname
'NIC':u'NU'	,	#Nicaragua
'FPY':u'PA'	,	#Paraguay
'PE' :u'PE'  ,	#Perú
'PA' :u'PM'  ,	#Panamá
'SPM':u'SB'	,	#San Pierre & Miquelon
'STL':u'ST'	,	#Santa Lucia
'TT' :u'TD'  ,	#Trinidad & Tabago
'TCO':u'TK'	,	#Turcos & Caicos
'U'  :u'UY'  ,	#Uruguay
'WV' :u'VC'  ,	#San Vincente & Granadinas
'YV' :u'VE'  ,	#Venezuela
'VRG':u'VI'	,	#Is. Vírgenes
'AUS':u'AS'	,	#Australia
'SOL':u'BP'	,	#Islas Salomón
'CSP':u'CW'	,	#Islas Cook
'FJI':u'FJ'	,	#Fiji
'FSP':u'FP'	,	#Polinesia
'KSP':u'KR'	,	#Kiribati
'NKP':u'NC'	,	#Nueva Caledonia
'NIU':u'NE'	,	#Niue
'NFI':u'NF'	,	#Islas Norfolk
'VAN':u'NH'	,	#Vanuatu
'NSP':u'NR'	,	#Nauru
'NZ' :u'NZ'  ,	#Nueva Zelanda
'PNG':u'PP'	,	#Papua Nueva Guinea
'PSP':u'PC'	,	#Pitcairn
'MSH':u'RM'	,	#Islas Marshall 
'TSP':u'TL'	,	#Tokelau
'TGA':u'TN'	,	#Tonga
'TVL':u'TV'	,	#Tuvalu
'WFP':u'WF'	,	#Wallis & Futuna
'WS' :u'WS'  ,	#Samoa-oeste
'AL' :u'AL'  ,	#Albania
'AND':u'AN'	,	#Andorra
'A'  :u'AU'  ,	#Austria
'WRS':u'BO'	,	#Bielorrusia
'B'  :u'BE'  ,	#Bélgica
'BHG':u'BK'	,	#Bosnia Herzegovina
'BG' :u'BU'  ,	#Bulgaria
'KRO':u'HR'	,	#Croacia
'CS' :u'EZ'  ,	#Checoslovaquia
'DK' :u'DA'  ,	#Dinamarca
'EST':u'EN'	,	#Estonia
'FOI':u'FO'	,	#Islas Faroe
'SF' :u'FI'  ,	#Finlandia
'F'  :u'FR'  ,	#Francia
'D'  :u'GM'  ,	#Alemania
'GR' :u'GR'  ,	#Grecia
'H'  :u'HU'  ,	#Hungría
'IS' :u'IC'  ,	#Islandia
'IRL':u'EI'	,	#Irlanda
'I'  :u'IT'  ,	#Italia
'LET':u'LG'	,	#Letonia
'FL' :u'LS'  ,	#Liechtenstein
'LIT':u'LH'	,	#Lituania
'L'  :u'LU'  ,	#Luxemburgo
'MAK':u'MK'	,	#Macedonia
'M'  :u'MT'  ,	#Malta
'MOL':u'MD'	,	#Moldavia
'MC' :u'MN'  ,	#Monaco
'NL' :u'NL'  ,	#Países Bajos
'N'  :u'NO'  ,	#Noruega
'PL' :u'PL'  ,	#Polonia
'P'  :u'PO'  ,	#Portugal
'R'  :u'RO'  ,	#Rumanía
'RSM':u'SM'	,	#San Marino
'YU' :u'YI'  ,	#Serbia & Montenegro
'SLO':u'SI'	,	#Eslovenia
'E'  :u'SP'  ,	#España
'S'  :u'SW'  ,	#Suecia
'CH' :u'SZ'  ,	#Suiza
'UKR':u'UP'	,	#Ucrania
'GBE':u'UK'	,	#Inglaterra
'SCO':u'UK'	,	#Inglaterra
'NIR':u'UK'	,	#Inglaterra
'SSR':u'RS'	}	#Rusia 
#US	Estados Unidos
usa = {
'New York': 'Nueva York',
'South Carolina': 'Carolina del Sur',
'North Carolina': 'Carolina del Norte'}

brackets = re.compile(' \[.*\]?')

class Console(gtk.VBox):
    def __init__(self,font):
        gtk.VBox.__init__(self, spacing=2)
        self.set_border_width(2)
        self.scrolledwin = gtk.ScrolledWindow()
        self.scrolledwin.show()
        self.pack_start(self.scrolledwin, padding=1)
        self.text = gtk.TextView()
        self.text.set_editable(True)
        self.text.set_wrap_mode(gtk.WRAP_WORD)
        self.scrolledwin.add(self.text)
        self.buffer = self.text.get_buffer() 
        self.end = self.buffer.create_mark('end',self.buffer.get_end_iter(),False)
        font = font.split(" ")[0].rstrip()+" 10"
        self.normal = self.buffer.create_tag('Normal', font=font, foreground='black')
        self.error = self.buffer.create_tag('Error', font=font, foreground='red') 
        self.warning = self.buffer.create_tag('Warning', font=font, foreground='blue') 
        self.buffer.insert_at_cursor(_("(La importacion puede tardar un poco...)\n")) 

def cust_cap(s):
    if s not in ['de','del','am','an','der','sous','im','bei','sur']:
        return s.capitalize()
    else:
        return s

def fix_tname(tn):
    tn = tn.replace(' ','_')
    if tn != '':
        while not tn[0].isalpha():
            tn = tn[1:]
        truetn = tn
        for let in tn:
            if not let.isalnum() and let != '_':
                truetn.replace(let,'')
        return truetn
    else:
        return tn


def parse_aaf(file,tname,con,sim,browser,encoding):
    from sqlite3 import DatabaseError
    import codecs
    doubt = []
    n = 0
    buf = con.buffer
    err = con.error; warn = con.warning
    try:
        f = codecs.open(file,'r',encoding)
    except IOError:
        buf.insert_with_tags(end,_("Error abriendo el archivo %s") % (file),err)
        return
    pending = False
    buf.set_text('')
    if not sim:
        curr.datab.create_table(tname)
        buf.insert_at_cursor(_("Creada tabla %s\n") % (tname))
    for line in f:
        start,end = buf.get_bounds()
        if line.startswith('#A93'): 
            loc = state.Locality()
            a = line[5:].split(',')
            if a[2] not in ['M','F'] and a[3] in ['M','F']:
                line = line.replace(',','',1)
                a = line[5:].split(',')
            last = a[0].strip(); first=a[1].strip()
            date=a[3][:-1]; time=a[4]
            city=a[5].strip(); ccode=a[6].strip()
            last=last.replace('*','')
            first = first.replace('*','')
            city = brackets.sub('',city)
            city = city.split('/')[0]
            city = city.split('-')[0]
            city = city.lower()
            city = ' '.join(map(lambda s:cust_cap(s), city.split(' '))) 
            try:
                ccode = ccodes[ccode].decode('utf8')
            except KeyError:
                if ccode.find('-') == -1:
                    ccode = brackets.sub('',ccode)
                    ccode = ccode.strip()
                    if ccode != '':
                        city = ccode + ' ' + city
                    ccode,count = a[7].split('-') 
                else:
                    ccode,count = ccode.split('-')
            city = city.strip()
            if city in mstar_bugloc:
                city = mstar_bugloc[city]
            if ccode.startswith('US'):
                loc=curr.datab.fetch_blindly_usacity(ccode[-2:],city,loc)
            else: 
                try:
                    ccode = ccodes[ccode]
                except KeyError,arg:
                    buf.insert_with_tags(end,
                            _("codigo pais no encontrado: %s\n") % (arg),err)
                    continue
                loc = curr.datab.fetch_blindly(ccode,city,loc) 
            if not isinstance(loc,state.Locality):
                buf.insert_with_tags(end,"%s\n" % (loc),err)
                pending = True
                continue
            curr.date.settz(loc.zone) 
            d,m,y = date.split('.')
            h,mi,s = time.split(':')
            dt = datetime.datetime(int(y),int(m),int(d),int(h),int(mi),int(s))
            dt = datetime.datetime.combine(dt.date(),dt.time())
            curr.loc = loc
            curr.date.setdt(dt)
            curr.person.first = first; curr.person.last = last
            curr.setchart()
            if not sim:
                try:
                    curr.datab.store_chart(tname, curr.charts['calc'])
                except DatabaseError:
                    curr.charts['calc'].first += str(n+1).rjust(3,'0')
                    curr.datab.store_chart(tname, curr.charts['calc'])
            buf.insert_at_cursor(_("Importando %s %s\n") % (first,last))
            con.text.scroll_to_mark(buf.get_insert(),0.0,True,0.0,0.0)
            n += 1
            while (gtk.events_pending()):
                gtk.main_iteration()
        elif pending and line.startswith('#B93'): 
            loc = state.Locality()
            b = line[5:].split(',')
            lt1,lt2 = b[1].split(':');lg1, lg2= b[2].split(':') 
            lgs = lg1[-3]; lg = lg1[0:-3]+lg1[-2:]+lg2
            if lgs == 'E': lgs = '-'
            else: lgs = ''
            lts = lt1[-3]; lt = lt1[0:-3]+lt1[-2:]+lt2
            if lts == 'S': lts = '-'
            else: lts = ''
            lgs += lg; lts += lt
            loc.longitud = lgs; loc.latitud = lts
            loc.latdec = degtodec(loc.latitud)
            loc.longdec = degtodec(loc.longitud)
            loc.city = city
            loc.country_code = ccode
            count = count.strip()
            if ccode.startswith('US'):
                loc.country = 'USA'
            elif count in ['Escocia']:
                loc.country = 'Gran Bretaña'
            else:
                loc.country = count 
            if ccode.startswith('US'):
                if count in ['New York','South Carolina','Noth Carolina']:
                    count = usa[count]
                st,code = curr.datab.get_usa_state_code(count)
                curr.datab.fetch_blindly_zone_usa(st,code,loc)
            else:
                curr.datab.fetch_blindly_zone(loc)
            pending = False
            doubt.append("%s %s: %s" % (first,last,city))
            curr.date.settz(loc.zone) 
            d,m,y = date.split('.')
            h,mi,s = time.split(':')
            dt = datetime.datetime(int(y),int(m),int(d),int(h),int(mi),int(s))
            dt = datetime.datetime.combine(dt.date(),dt.time())
            curr.loc = loc
            curr.date.setdt(dt)
            curr.person.first = first; curr.person.last = last
            curr.setchart()
            if not sim:
                try:
                    curr.datab.store_chart(tname, curr.charts['calc'])
                except DatabaseError:
                    curr.charts['calc'].first += str(n+1).rjust(3,'0')
                    curr.datab.store_chart(tname, curr.charts['calc'])
            buf.insert_at_cursor(_("Importando %s %s\n") % (first,last))
            n += 1
            con.text.scroll_to_mark(buf.get_insert(),0.0,True,0.0,0.0)
            while (gtk.events_pending()):
                gtk.main_iteration()
    #end
    if not sim:
        browser.tables.emit('changed')
        browser.relist(tname)
    else:
        buf.insert_at_cursor('\nImportacion terminada en modo simulacion\n')
    start,end = buf.get_bounds()
    buf.create_mark('mess',end,True)
    buf.insert_with_tags(end,'\n*******\n',warn)
    buf.insert_at_cursor(_("Cartas importadas: %s; dudosas: %s") % (n,len(doubt)))
    buf.insert_at_cursor('(%.2f%%) \n' % (100*len(doubt)/float(n)))
    buf.insert_at_cursor(_("Las cartas siguientes fueron importadas sin encontrar\n"))
    buf.insert_at_cursor(_("la localidad correspondiente, y la zona horaria sera\n"))
    buf.insert_at_cursor(_("probablemente incorrrecta. Puede editar este panel,\n"))
    buf.insert_at_cursor(_("y copiar su contenido (menu clic derecho).")) 
    start,end = buf.get_bounds()
    buf.insert_with_tags(end,'\n*******\n',warn)
    for d in doubt:
        buf.insert_with_tags(end,'%s\n' % d,warn)
    con.text.scroll_to_mark(buf.get_mark('mess'),0.0,True,0.0,0.0)


def dlg_response(ibut,entry,tentry,con,but,enc,browser):
    file = ''; tn = ''
    codes = ['cp1252','utf-8']
    file = entry.get_text()
    tname = tentry.get_text()
    tn = fix_tname(tname)
    if entry.get_text() == '' or tn == '':
        return
    else: 
        tablelist = curr.datab.get_databases() 
        simul = but.get_active()
        if not simul:
            if tn in tablelist:
                result = replacedialog(tn)
                if result != gtk.RESPONSE_OK:
                    return 
        encoding = codes[enc.get_active()]
        #print encoding
        parse_aaf(file,tn,con,simul,browser,encoding)

def on_browse_but(but,entry):
    dialog = gtk.FileChooserDialog("Abrir archivo...",
                                None,
                                gtk.FILE_CHOOSER_ACTION_OPEN,
                                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)

    filter = gtk.FileFilter()
    filter.set_name(_("Archivo AAF"))
    filter.add_mime_type("text/plain")
    filter.add_pattern("*.aaf")
    dialog.add_filter(filter)
    if sys.platform == 'win32':
        import winshell
        dialog.set_current_folder(winshell.my_documents())
    else: 
        dialog.set_current_folder(os.path.expanduser("~"))

    filename = None
    response = dialog.run()
    if response == gtk.RESPONSE_OK:
        filename = dialog.get_filename()
    elif response == gtk.RESPONSE_CANCEL:
        pass
    dialog.destroy()
    if filename is not None and filename != '':
        entry.set_text(filename) 
    return

def replacedialog(tbl):
    msg = _("La tabla %s existe. Reemplazarla, perdiendo los datos?") % tbl
    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
            gtk.MESSAGE_WARNING,
            gtk.BUTTONS_OK_CANCEL, msg);
    result = dialog.run()
    dialog.destroy()
    return result


def export_chart(ch):
    aaf = "%s,%s,%s,%s,%s,%s,%s,%s,%s"
    aaf = aaf % (ch.last,ch.first,ch.date,ch.city,ch.region,ch.country,ch.zone,ch.latitud,ch.longitud)
    return aaf

#A93:Afa144,Edgar Allan,M,19.01.1809g,01:48:00,Boston,USMA-Massachusetts 
#B93:*,42N21:00,071W03:00,05hw00,0

class ImportPanel(gtk.HBox):
    def __init__(self,parent):
        global curr
        curr = parent.boss.get_state()
        browser = parent.mpanel.browser
        gtk.HBox.__init__(self)
        cons = Console(browser.font)
        
        frame = gtk.Frame()
        table = gtk.Table(2,4,True)
        label = gtk.Label(_('Importar archivo: '))
        entry = gtk.Entry()
        button = gtk.Button(_('Examinar'))
        button.connect('clicked',on_browse_but,entry)
        table.attach(label,0,1,0,1)
        table.attach(entry,1,2,0,1)
        table.attach(button,2,3,0,1)
        
        label = gtk.Label(_('Nombre tabla: '))
        tentry = gtk.Entry()
        tentry.set_text('importemp')
        button = gtk.CheckButton(_('Simular'))
        button.set_active(True)
        table.attach(label,0,1,1,2)
        table.attach(tentry,1,2,1,2)
        table.attach(button,2,3,1,2)
        
        encoding = gtk.RadioButton(None,'Win-1252')
        encoding.set_active(True)
        table.attach(encoding,3,4,0,1)
        encoding = gtk.RadioButton(encoding,'utf-8')
        table.attach(encoding,3,4,1,2)
    
        frame.add(table)
        vbox = gtk.VBox()
        vbox.pack_start(frame,False,False)
        vbox.pack_start(cons) 
        ibutton = gtk.Button(_('Importar'))
        ibutton.connect("clicked",dlg_response,entry,tentry,cons,button,encoding,browser)
        hbox = gtk.HBox()
        hbox.pack_end(ibutton,False,False)    
        vbox.pack_start(hbox,False,False)    
        frame = gtk.Frame()
        frame.set_border_width(6)
        frame.add(vbox)
        self.add(frame)
