# -*- coding: utf-8 -*-
from chart import Chart
import database as datab
from extensions.path import path

ccodes = {
u'AF': u'AFG'	,	#Afganistán
u'AM': u'ARM'	,	#Armenia
u'AJ': u'ASB'	,	#Azerbaiján
u'BA': u'BRN'	,	#Bahrain
u'BG': u'BD'    ,	#Bangla Desh
u'BT': u'BHU'	,	#Bhután
u'BX': u'BRU'	,	#Brunei
u'CB': u'K'     ,	#Camboya
u'CH': u'TJ'    ,	#China
u'CY': u'CY'    ,	#Chipre
u'GG': u'GRG'	,	#Georgia
u'HK': u'HKG'	,	#Hong Kong
u'IN': u'IND'	,	#India
u'ID': u'RI'    ,	#Indonesia
u'IR': u'IR'    ,	#Irán
u'IZ': u'IRQ'	,	#Irak
u'IS': u'IL'    ,	#Israel
u'JA': u'J'     ,	#Japón
u'JO': u'JOR'	,	#Jordania
u'KZ': u'KAZ'	,	#Kazajstán
u'KN': u'KOR'	,	#Corea del Norte
u'KS': u'ROK'	,	#Corea del Sur
u'KU': u'KWT'	,	#Kuwait
u'KG': u'KIR'	,	#Kirguizistán
u'LA': u'LAO'	,	#Laos
u'LE': u'RL'    ,	#Líbano
u'MY': u'MAL'	,	#Malasia
u'MV': u'MDV'	,	#Maldivas
u'MG': u'MOG'	,	#Mongolia
u'BM': u'MYA'	,	#Myanmar (Birmania)
u'NP': u'NEP'	,	#Nepal
u'MU': u'OMN'	,	#Omán
u'PK': u'PAK'	,	#Pakistán
u'RP': u'RP'    ,	#Filipinas
u'QA': u'Q'     ,	#Qatar
u'SA': u'SA'    ,	#Arabia Saudita
u'SN': u'SGP'	,	#Singapur
u'CE': u'CL'    ,	#Sri Lanka
u'SY': u'SYR'	,	#Siria
u'TW': u'RC'    ,	#Taiwán
u'TI': u'TAJ'	,	#Tadschikistan
u'TH': u'THA'	,	#Tailandia
u'TU': u'TR'    ,	#Turquía
u'TX': u'TUR'	,	#Turkmenistan
u'AE': u'UAE'	,	#Emiratos Arabes
u'UZ': u'UZB'	,	#Uzbekistan
u'VM': u'VN'    ,	#Vietnam
u'YM': u'YMD'	,	#Yemen
u'AG': u'DZ'    ,	#Argelia
u'AO': u'ANG'	,	#Angola
u'BN': u'RPH'	,	#Benin
u'BC': u'RB'    ,	#Botswana
u'UV': u'BF'    ,	#Burkina Faso
u'BY': u'BU'    ,	#Burundi
u'CM': u'CAM'	,	#Camerun
u'CV': u'KVR'	,	#Cabo Verde
u'CT': u'RCA'	,	#Central-Africa
u'CD': u'CHA'	,	#Chad
u'CN': u'KOM'	,	#Comoros
u'CF': u'RCB'	,	#Congo (Brazzaville)
u'CG': u'ZR'    ,	#Congo (Kinshasa)
u'DJ': u'DH'    ,	#Djibouti
u'EG': u'ET'    ,	#Egipto
u'EK': u'AQG'	,	#Guinea ecuatorial
u'ET': u'ETH'	,	#Etiopía
u'GB': u'GAB'	,	#Gabón
u'GA': u'GAM'	,	#Gambia
u'GH': u'GH'    ,	#Ghana
u'GV': u'GUI'	,	#Guinea
u'PU': u'GBA'	,	#Guinea-Bissau
u'IV': u'CI'    ,	#Costa de Marfil
u'KE': u'EAK'	,	#Kenya
u'LT': u'LS'    ,	#Lesotho
u'LI': u'LB'    ,	#Liberia
u'LY': u'LAR'	,	#Libia
u'MA': u'RM'    ,	#Madagascar
u'MI': u'MW'    ,	#Malawi
u'ML': u'RMM'	,	#Mali
u'MR': u'RIM'	,	#Mauritania
u'MP': u'MS'    ,	#Mauricio
u'MF': u'MY'    ,	#Mayotte
u'MO': u'MA'    ,	#Marruecos
u'MZ': u'MOZ'	,	#Mozambique
u'WA': u'NAB'	,	#Namibia
u'NG': u'RN'    ,	#Níger
u'NI': u'WAN'	,	#Nigeria
u'RE': u'REU'	,	#Reunión
u'RW': u'RWA'	,	#Ruanda
u'SH': u'SHA'	,	#Santa Helena
u'TP': u'STP'	,	#Santo Tomé & Príncipe
u'SG': u'SN'    ,	#Senegal
u'SE': u'SY'    ,	#Seychelles
u'SL': u'WAL'	,	#Sierra Leona
u'SO': u'SP'    ,	#Somalia
u'SF': u'ZA'    ,	#Sudáfrica
u'SU': u'FS'    ,	#Sudán
u'WZ': u'SD'    ,	#Swazilandia
u'TZ': u'EAT'	,	#Tanzania
u'TO': u'TG'    ,	#Togo
u'TS': u'TN'    ,	#Túnez
u'UG': u'EAV'	,	#Uganda
u'ZA': u'Z'     ,	#Zambia
u'ZI': u'ZW'    ,	#Zimbabwe
u'AC': u'ANT'	,	#Antigua & Barbuda
u'AR': u'RA'    ,	#Argentina
u'AV': u'AGU'	,	#Anguilla
u'BB': u'BDS'	,	#Barbados
u'BD': u'BPA'	,	#Bermudas
u'BF': u'BS'    ,	#Bahamas
u'BH': u'BH'    ,	#Belice
u'BL': u'BOL'	,	#Bolivia
u'BR': u'BR'    ,	#Brasil
u'CA': u'CDN'	,	#Canadá
u'CI': u'RCH'	,	#Chile
u'CJ': u'CAY'	,	#Islas Caimán
u'CO': u'CO'    ,	#Colombia
u'CS': u'CR'    ,	#Costa Rica
u'CU': u'C'     ,	#Cuba
u'DO': u'WD'    ,	#Dominica
u'DR': u'DOM'	,	#República Dominicana
u'EC': u'EC'    ,	#Ecuador
u'ES': u'ES'    ,	#El Salvador
u'FG': u'FGU'	,	#Guayana Fr.
u'FK': u'FGB'	,	#Islas Malvinas
u'GJ': u'WG'    ,	#Granada
u'GL': u'GRO'	,	#Groenlandia
u'GP': u'GKA'	,	#Guadalupe
u'GT': u'GCA'	,	#Guatemala
u'GY': u'GUY'	,	#Guyana
u'HA': u'RH'    ,	#Haití
u'HO': u'HON'	,	#Honduras
u'JM': u'JA'    ,	#Jamaica
u'MB': u'MQU'	,	#Martinique
u'MH': u'MTT'	,	#Montserrat
u'MX': u'MEX'	,	#México
u'NS': u'SME'	,	#Suriname
u'NU': u'NIC'	,	#Nicaragua
u'PA': u'FPY'	,	#Paraguay
u'PE': u'PE'    ,	#Perú
u'PM': u'PA'    ,	#Panamá
u'SB': u'SPM'	,	#San Pierre & Miquelon
u'ST': u'STL'	,	#Santa Lucia
u'TD': u'TT'    ,	#Trinidad & Tabago
u'TK': u'TCO'	,	#Turcos & Caicos
u'UY': u'U'     ,	#Uruguay
u'VC': u'WV'    ,	#San Vincente & Granadinas
u'VE': u'YV'    ,	#Venezuela
u'VI': u'VRG'	,	#Is. Vírgenes
u'AS': u'AUS'	,	#Australia
u'BP': u'SOL'	,	#Islas Salomón
u'CW': u'CSP'	,	#Islas Cook
u'FJ': u'FJI'	,	#Fiji
u'FP': u'FSP'	,	#Polinesia
u'KR': u'KSP'	,	#Kiribati
u'NC': u'NKP'	,	#Nueva Caledonia
u'NE': u'NIU'	,	#Niue
u'NF': u'NFI'	,	#Islas Norfolk
u'NH': u'VAN'	,	#Vanuatu
u'NR': u'NSP'	,	#Nauru
u'NZ': u'NZ'    ,	#Nueva Zelanda
u'PP': u'PNG'	,	#Papua Nueva Guinea
u'PC': u'PSP'	,	#Pitcairn
u'RM': u'MSH'	,	#Islas Marshall 
u'TL': u'TSP'	,	#Tokelau
u'TN': u'TGA'	,	#Tonga
u'TV': u'TVL'	,	#Tuvalu
u'WF': u'WFP'	,	#Wallis & Futuna
u'WS': u'WS'    ,	#Samoa-oeste
u'AL': u'AL'    ,	#Albania
u'AN': u'AND'	,	#Andorra
u'AU': u'A'     ,	#Austria
u'BO': u'WRS'	,	#Bielorrusia
u'BE': u'B'     ,	#Bélgica
u'BK': u'BHG'	,	#Bosnia Herzegovina
u'BU': u'BG'    ,	#Bulgaria
u'HR': u'KRO'	,	#Croacia
u'EZ': u'CS'    ,	#Checoslovaquia
u'DA': u'DK'    ,	#Dinamarca
u'EN': u'EST'	,	#Estonia
u'FO': u'FOI'	,	#Islas Faroe
u'FI': u'SF'    ,	#Finlandia
u'FR': u'F'     ,	#Francia
u'GM': u'D'     ,	#Alemania
u'GR': u'GR'    ,	#Grecia
u'HU': u'H'     ,	#Hungría
u'IC': u'IS'    ,	#Islandia
u'EI': u'IRL'	,	#Irlanda
u'IT': u'I'     ,	#Italia
u'LG': u'LET'	,	#Letonia
u'LS': u'FL'    ,	#Liechtenstein
u'LH': u'LIT'	,	#Lituania
u'LU': u'L'     ,	#Luxemburgo
u'MK': u'MAK'	,	#Macedonia
u'MT': u'M'     ,	#Malta
u'MD': u'MOL'	,	#Moldavia
u'MN': u'MC'    ,	#Monaco
u'NL': u'NL'    ,	#Países Bajos
u'NO': u'N'     ,	#Noruega
u'PL': u'PL'    ,	#Polonia
u'PO': u'P'     ,	#Portugal
u'RO': u'R'     ,	#Rumanía
u'SM': u'RSM'	,	#San Marino
u'YI': u'YU'    ,	#Serbia & Montenegro
u'SI': u'SLO'	,	#Eslovenia
u'SP': u'E'     ,	#España
u'SW': u'S'     ,	#Suecia
u'SZ': u'CH'    ,	#Suiza
u'UP': u'UKR'	,	#Ucrania
u'UK': u'GBE'	,	#Inglaterra
u'UK': u'SCO'	,	#Inglaterra
u'UK': u'NIR'	,	#Inglaterra
u'RS': u'SSR'		#Rusia 
}

aaf_record = dict(name='',fname='',sex='*',date='',time='',place='',country='')
headA = "#A93"
sex = '*'

def export_chart(chart):
    name = chart.last if chart.last else '*'
    a93 = ":".join([headA,name])
    fname = chart.first if chart.first else '*'
    place = chart.city
    date,_,time = chart.date.partition('T')
    date = ".".join(reversed([d.lstrip('0') for d in date.split('-')])) 
    time = time[:5]
    country = ccodes[datab.get_code_from_name(chart.country)]
    achunk = ",".join([a93,fname,sex,date,time,place,country])
    return achunk

def export_table(table):
    chlist = datab.get_chartlist(table)
    chart = Chart()
    chunks = []
    for id,_,_ in chlist:
        datab.load_chart(tname, id, chart) 
        chunks.append(export_chart(chart))
    return chunks

if __name__ == '__main__':
    datab.easy_connect()
    tname = 'personal'
    chunks = export_table(tname)
    aafile = path.joinpath(path.expanduser(path('~')),"%s.aaf" % tname)
    f = open(aafile,'w')
    for ch in chunks:
        f.write(ch.encode('utf-8'))
        f.write('\n')
    f.close()
    #print chunks



