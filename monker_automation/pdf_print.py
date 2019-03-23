#!/usr/bin/env python3

# import random
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from monker_automation.views import print_view
from monker_automation.views import get_view
from monker_automation.utils import *
from reportlab.pdfgen import canvas
import os
import shutil


def print_pdf(line=[]):
    pdf = os.path.join(DEFAULT_REPORT_DIRECTORY, VIEW_PDF_NAME)
    c = canvas.Canvas(pdf)
    image = os.path.join(DEFAULT_REPORT_DIRECTORY, RANGE_PNG_NAME)
    c.drawImage(image, 10, 10, 560, 300)
    image = os.path.join(DEFAULT_REPORT_DIRECTORY, STRATEGY_PNG_NAME)
    c.drawImage(image, 10, 320, 560, 380)
    image = os.path.join(DEFAULT_REPORT_DIRECTORY, TABLE_PNG_NAME)
    c.drawImage(image, 35, 700, 150, 150)
    if not QUIZ:
        image = os.path.join(DEFAULT_REPORT_DIRECTORY, RANGE_HEADER_PNG_NAME)
        c.drawImage(image, 225, 755, 300, 40)
    if line:
        c.setFont("Helvetica", 8)
        c.drawString(200, 725, "-".join(line))
        #c.bookmarkPage("-".join(line))
        #c.addOutlineEntry("-".join(line),"-".join(line), 0, 0)
    c.save()


def print_all_views(board):
    # print views into monker view folder and to Analysis Folder / views/
    for view_type in VIEW_TYPES[:-1]:
        view = get_view(board, view_type)
        # print view to monker view folder (just with VIEW_TYPE name)
        print_view(view, view_type, VIEW_FOLDER, "")
        # print view to analysis folder with board - type.txt
        print_view(view, view_type, DEFAULT_REPORT_VIEW_DIR,
                   board.replace(" ", "-"))


def add_analysis_to_report(report_name=REPORT_PDF_NAME,bookmark=DEFAULT_BOOKMARK):

    merger = PdfFileMerger()
    #writer = PdfFileWriter()
    report_filename = os.path.join(
        DEFAULT_REPORT_DIRECTORY, report_name)
    analysis_filename = os.path.join(
        DEFAULT_REPORT_DIRECTORY, VIEW_PDF_NAME)

    bookmark=bookmark.replace("CHECK","X")
    bookmark=bookmark.replace("CALL","C")
    bookmark=bookmark.replace("BET ","B")
    bookmark=bookmark.replace("RAISE ", "R")

    try:
        with open(report_filename, 'rb') as f:
            pdf = PdfFileReader(f)
            num_pages=pdf.getNumPages()
            outline=pdf.getOutlines()
            merger.append(pdf,import_bookmarks=False)
    except IOError:  # seems to be first page of the report
        with open(analysis_filename, 'rb') as f:
            writer=PdfFileWriter()
            writer.appendPagesFromReader(PdfFileReader(f))
            writer.addBookmark(bookmark,0)
            with open(report_filename, 'wb') as o:
                writer.write(o)
        #shutil.copy(analysis_filename, report_filename)
        return

    for page in range(0,len(outline)):
        merger.addBookmark(outline[page].title,page)

    with open(analysis_filename, 'rb') as f:
        merger.append(PdfFileReader(f),bookmark)

    merger.write(report_filename)