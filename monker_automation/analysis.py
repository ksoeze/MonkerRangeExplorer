#!/usr/bin/env python3
from monker_automation.pdf_print import print_pdf, add_analysis_to_report, print_all_views
from monker_automation.utils import *
from monker_automation.gui import read_situation_and_save_ranges
from monker_automation.range import get_view_results
from monker_automation.views import get_view, combine_views
from monker_automation.plot import plot_default
from monker_automation.plot import plot_range_distribution
import logging


def print_result_header(header, gui_log, result_filename=DEFAULT_VIEW_RESULT_FILENAME):
    with open(result_filename, 'a') as f:
        f.write(
            "-------------------------------------------------------------------------------------------------------------------------\n")
        f.write(
            "-------------------------------------------------------------------------------------------------------------------------\n")
        f.write(header + "\n")
        f.write("Board: {}\n".format(gui_log["board"]))
        f.write("LINE:\n {}".format(gui_log["line"]))
        f.write("\n\nRESULTS: \n\n")

def current_spot(view_type1=VIEW_TYPES[0], view_type2=None, ig_first_entry=True, mega=False, print_views=True):
    infos = read_situation_and_save_ranges()
    board = infos["board"]
    actions = infos["actions"]

    bookmark_str = board + infos["line"].replace("\n","->")
    if print_views:
        print_all_views(board)

    if view_type2 == None:
        view = get_view(board, view_type1)
        total_results, action_results = get_view_results(actions, view)
        plot_default(total_results, action_results, infos["actions"])
        plot_range_distribution(total_results, action_results, infos["actions"])
        print_pdf()
        add_analysis_to_report(bookmark=bookmark_str)
        if QUIZ == True: # UGLY HACK prints solution to report ...NOT FOR SCRIPT RUN FOR NOW JUST STANDALONE
            plot_default(total_results, action_results, infos["actions"],False)
            plot_range_distribution(total_results, action_results, infos["actions"],False)
            print_pdf()
            add_analysis_to_report(bookmark=bookmark_str,quiz=False)
        return

    views, megaview = combine_views(board,view_type1, view_type2,ig_first_entry)
    if mega and megaview != []:
        total_results, action_results = get_view_results(actions, megaview)
        plot_default(total_results, action_results, infos["actions"])
        plot_range_distribution(total_results, action_results, infos["actions"])
        print_pdf()
        add_analysis_to_report(bookmark=bookmark_str)
    for view in views:
        total_results, action_results = get_view_results(actions, view)
        plot_default(total_results, action_results, infos["actions"])
        plot_range_distribution(total_results, action_results, infos["actions"])
        print_pdf()
        add_analysis_to_report(bookmark=bookmark_str)
    return

def test():
    logger = logging.getLogger()
    logger.setLevel("DEBUG")
    board = "KdJh5h4c4s"
    board = "KdJh5h"
    current_spot()

if (__name__ == '__main__'):
    test()
