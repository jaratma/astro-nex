# -*- coding: utf-8 -*-
from scripts import Script
       
class PdfBatch(Script):
    def run(self,*arg,**kw):
        from .. surfaces.pdfsurface import DrawPdf
        if kw['table']:
            DrawPdf.pg_table_batch(kw['table'])
        else:
            DrawPdf.simple_batch()

pdfbatch = PdfBatch
