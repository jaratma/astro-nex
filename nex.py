#!/usr/bin/python
from optparse import OptionParser
parser = OptionParser()

parser.add_option("-c", "--console", action="store_true", default=False)
(options, args) = parser.parse_args()

from astronex.extensions.path import path
appath = path.getcwd() 
from astronex import nex
nex.main(appath,options.console)
