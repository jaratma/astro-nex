# -*- coding: utf-8 -*-
from scripts import Script
       
class PngPlangram(Script):
    def run(self,*arg,**kw):
        from .. surfaces.pngsurface import DrawPng
        DrawPng.simple_batch()

pngplangram = PngPlangram 
