#!/usr/bin/env python3

# import random
from PyPDF2 import PdfFileMerger, PdfFileReader
from monker_automation.views import print_view
from monker_automation.views import get_view
from monker_automation.analysis import current_view
from monker_automation.utils import *
from reportlab.pdfgen import canvas
# from reportlab.lib.units import inch
# from monker_automation.analysis import current_view
import os
import shutil


def print_pdf():
    pdf = os.path.join(DEFAULT_REPORT_DIRECTORY, VIEW_PDF_NAME)
    c = canvas.Canvas(pdf)
    image = os.path.join(DEFAULT_REPORT_DIRECTORY, RANGE_PNG_NAME)
    c.drawImage(image, 10, 10, 560, 300)
    image = os.path.join(DEFAULT_REPORT_DIRECTORY, STRATEGY_PNG_NAME)
    c.drawImage(image, 10, 320, 560, 380)
    image = os.path.join(DEFAULT_REPORT_DIRECTORY, TABLE_PNG_NAME)
    c.drawImage(image, 35, 700, 150, 150)
    image = os.path.join(DEFAULT_REPORT_DIRECTORY, RANGE_HEADER_PNG_NAME)
    c.drawImage(image, 225, 755, 300, 40)
    c.save()


def print_all_views(board):
    # print views into monker view folder and to Analysis Folder / views/
    for view_type in VIEW_TYPES:
        view = get_view(board, view_type)
        # print view to monker view folder (just with VIEW_TYPE name)
        print_view(view, view_type, VIEW_FOLDER, "")
        # print view to analysis folder with board - type.txt
        print_view(view, view_type, DEFAULT_REPORT_VIEW_DIR,
                   board.replace(" ", "-"))


def add_analysis_to_report():

    merger = PdfFileMerger()
    report_filename = os.path.join(
        DEFAULT_REPORT_DIRECTORY, REPORT_PDF_NAME)
    analysis_filename = os.path.join(
        DEFAULT_REPORT_DIRECTORY, VIEW_PDF_NAME)

    try:
        with open(report_filename, 'rb') as f:
            merger.append(PdfFileReader(f))
    except IOError:  # seems to be first page of the report
        shutil.copy(analysis_filename, report_filename)
        return

    with open(analysis_filename, 'rb') as f:
        merger.append(PdfFileReader(f))

    merger.write(report_filename)


def do_analysis():
    results = current_view()
    board = results["board"]
    # generate all views:
    print_all_views(board)
    print_pdf()
    add_analysis_to_report()
