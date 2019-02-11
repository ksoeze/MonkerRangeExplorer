#!/usr/bin/env python3

# import random
from PyPDF2 import PdfFileWriter, PdfFileReader
from monker_automation.utils import *
import os

def all_pdf_files():
    files = [f for f in os.listdir(DEFAULT_REPORT_MATCHER_DIRECTORY)]
    files = [f for f in files if f.endswith((".pdf",".PDF"))]
    return files

def reorganise_pdfs():
    pdf_files=all_pdf_files()
    if pdf_files == []:
        return
    open_files = []
    input_files = []
    output_files = []
    for item in pdf_files:
        f = open(os.path.join(DEFAULT_REPORT_MATCHER_DIRECTORY,item), "rb")
        input_files.append(PdfFileReader(f))
        open_files.append(f)

    pages = input_files[0].getNumPages()
    for i in range(pages):
        output_files.append(PdfFileWriter())

    for i in range(pages):
        for input in input_files:
            output_files[i].addPage(input.getPage(i))

    for i in range(len(output_files)):
        with open(os.path.join(DEFAULT_REPORT_MATCHER_DIRECTORY,"Page"+str(i+1)), "wb") as f:
            output_files[i].write(f)
    for f in open_files:
        f.close()
    return

if (__name__ == '__main__'):
    reorganise_pdfs()




