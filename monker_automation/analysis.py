#!/usr/bin/env python3

from monker_automation.utils import *
from monker_automation.gui import enter_sequence_and_save_ranges
from monker_automation.gui import read_situation_and_save_ranges
from monker_automation.range import strategy_overview
from monker_automation.range import org_print_result_matrix
from monker_automation.range import get_view_results
from monker_automation.views import get_view
from monker_automation.views import print_view
from monker_automation.views import view_item_to_str
from monker_automation.plot import plot_default
from monker_automation.plot import plot_range_distribution
import logging
import pickle

import matplotlib.pyplot as plt


def print_result_header(header, gui_log, result_filename=DEFAULT_VIEW_RESULT_FILENAME):
    with open(result_filename, 'a') as f:
        f.write("-------------------------------------------------------------------------------------------------------------------------\n")
        f.write("-------------------------------------------------------------------------------------------------------------------------\n")
        f.write(header+"\n")
        f.write("Board: {}\n".format(gui_log["board"]))
        f.write("LINE:\n {}".format(gui_log["line"]))
        f.write("\n\nRESULTS: \n\n")


# def default_view(sequence, actions, board, enter_cards="", result_filename=DEFAULT_VIEW_RESULT_FILENAME):
#     # generate view
#     view = get_view(board, VIEW_TYPES[0])
#     print_view(view, VIEW_TYPES[0], board)
#     debug = enter_sequence_and_save_ranges(sequence, actions, enter_cards)
#     # print(debug)
#     results = strategy_overview(actions, view)
#     print_result_header("General Overview", debug)
#     org_print_result_matrix(results, result_filename)

def default_view(sequence, actions, board, enter_cards="", result_filename=DEFAULT_VIEW_RESULT_FILENAME):
    view = get_view(board, VIEW_TYPES[0])
    print_view(view, VIEW_TYPES[0], board)
    debug = enter_sequence_and_save_ranges(sequence, actions, enter_cards)
    debug = ""
    total_results, action_results = get_view_results(actions, view)

    output_table = []
    first_line = ["Description"]+total_results["v_str"]
    output_table.append(first_line)
    # Total
    output_table.append(["Total %"] + total_results["r"])
    # Total cum
    output_table.append([" "] + total_results["r_cum"])
    for action in action_results:
        # percent of action with view entry
        output_table.append([action]+action_results[action]["p"])
        # range distribution of this action
        output_table.append(["Relativ %"]+action_results[action]["r"])
        # range distribution of this action cum
        output_table.append([" "]+action_results[action]["r_cum"])
    # print_result_header("Genera Overview", debug)
    # transpose table
    output_table = [*zip(*output_table)]
    # org_print_result_matrix(output_table, result_filename)
    titel = "KdJh5h-4c4s - 3 Barrel Strategy TEST"
    plot_default(
        titel, total_results, action_results, list(reversed(actions)))
    plot_range_distribution(titel, total_results, action_results, actions)


def current_view():
    infos = read_situation_and_save_ranges()
    # with open("infos_pickle", "wb") as f:
    #     pickle.dump(infos, f)
    # with open("infos_pickle", "rb") as f:
    #    infos = pickle.load(f)
    board = infos["board"]
    view = get_view(board, VIEW_TYPES[0])
    actions = infos["actions"]

    total_results, action_results = get_view_results(actions, view)

    # with open("results_pickle", "wb") as f:
    #     pickle.dump((total_results, action_results), f)
    # with open("results_pickle", "rb") as f:
    #    total_results, action_results = pickle.load(f)
    default_view = plot_default(total_results, action_results, actions)
    range_view = plot_range_distribution(
        total_results, action_results, actions)
    return infos


def run_out_analysis(sequences, board, enter_cards="", player="", result_filename=DEFAULT_VIEW_RESULT_FILENAME):
    # generate view
    view = get_view(board, VIEW_TYPES[1])
    print_view(view, VIEW_TYPES[1], board)
    results = []
    results.append([player]+[view_item_to_str(i) for i in view] + ["Other"])
    for item in sequences:
        line_description = item[0]
        sequence = item[1]
        actions = item[2]
        debug = enter_sequence_and_save_ranges(sequence, actions, enter_cards)
        print(debug)  # print to logfile?
        total_results, action_results = get_view_results(actions, view)
        line = [line_description]+total_results[0][1:]  # remove total result
        results.append(line)
        line = [""]+total_results[1][1:]  # cumulative
        results.append(line)
        # print infos for action if wanted
        if len(item) == 4:
            print_action = item[3]
            line = [print_action]+action_results[print_action][0][1:]
            results.append(line)
            # if wanted print range % for this action
            line = ["%"]+action_results[print_action][1][1:]
            results.append(line)
            # if wanted print cummulative_counts
            line = [" "]+action_results[print_action][2][1:]
            results.append(line)
        line = ["-"]*len(total_results[0])  # for better visibility in org mode
        results.append(line)

    print_result_header("Runout Analysis for Player: {}".format(
        player), {"board": board, "line": "..."})
    org_print_result_matrix(results, result_filename)


def view_matrix(sequence, actions, board, general_view=VIEW_TYPES[1], subview=VIEW_TYPES[2], enter_cards="", result_filename=DEFAULT_VIEW_RESULT_FILENAME):
    view = get_view(board, general_view)
    for item in view:
        if len(item) == 0:
            logging.warning(
                "EMPTY item in view with type {} on board {}".format(general_view, board))
        elif type(item[0]) == list:
            logging.error("Combined view (fe xx:hh) not supported in view matrix analysis ( view: {} board: {})".format(
                general_view, board))
            return
    results = []
    results.append(["Combination", "Total"] + [view_item_to_str(i)
                                               for i in view] + ["Other"])
    debug = enter_sequence_and_save_ranges(sequence, actions, enter_cards)
    print(debug)

    total_results, action_results = get_view_results(actions, view)
    results.append(["Total"] + total_results[0])

    subview_view = get_view(board, subview)
    total_subview_results, action_subview_results = get_view_results(
        actions, subview_view, False)
    for item in total_subview_results:
        logging.debug(item)

    for index in range(len(subview_view)):
        if len(subview_view[index]) == 0:
            logging.warning(
                "EMPTY item in view with type {} on board {}".format(subview, board))
        elif type(subview_view[index][0]) == list:
            logging.error(
                "Combined view (fe xx:hh) not supported in view matrix analysis ( view: {} board: {})".format(subview, board))
            return
        new_view = [[v, subview_view[index]]
                    for v in view] + [subview_view[index]]
        logging.debug("NEW VIEW:")
        for item in new_view:
            logging.debug(item)
        total_results, action_results = get_view_results(actions, new_view)
        line = [view_item_to_str(subview_view[index]),
                total_subview_results[0][index+1]]
        line += total_results[0][1: -1]
        results.append(line)

    exclude_list = [hand for rng in subview_view for hand in rng]
    # logging.debug(view)
    # logging.debug(exclude_list)
    view = [exclude_list]+view
    other_total_results, other_action_results = get_view_results(
        actions, view)
    # for item in other_total_results:
    #     print(item)
    other_total = '{}'.format(100 - float(other_total_results[0][1]))
    line = ["Other"] + [other_total] + other_total_results[0][2:]
    results.append(line)
    return results


def test_runout_analysis():
    board = "KdJh5hQs3c"
    enter_cards = "Qs3c"

    # lines for BB
    sequence = []
    sequence.append(["Overall",
                     [("CHECK", "FLOP"), ("CHECK", "FLOP")],
                     ("CHECK", "BET")])
    sequence.append(["X/C",
                     [("CHECK", "FLOP"), ("BET", "FLOP"), ("CALL", "FLOP")],
                     ("CHECK", "BET")])
    sequence.append(["X/C->X/C",
                     [("CHECK", "FLOP"), ("BET", "FLOP"), ("CALL", "FLOP"),
                      ("CHECK", "TURN"), ("BET", "TURN"), ("CALL", "TURN")
                      ],
                     ("CHECK", "BET")])
    sequence.append(["X/R",
                     [("CHECK", "FLOP"), ("BET", "FLOP"),
                      ("RAISE", "FLOP"), ("CALL", "FLOP")],
                     ("CHECK", "BET")])
    sequence.append(["X->B",
                     [("CHECK", "FLOP"), ("CHECK", "FLOP"),
                      ("BET", "TURN"), ("CALL", "TURN")],
                     ("CHECK", "BET"),
                     "BET"])
    sequence.append(["X->X/C",
                     [("CHECK", "FLOP"), ("CHECK", "FLOP"),
                      ("CHECK", "TURN"), ("BET", "TURN"), ("CALL", "TURN")],
                     ("CHECK", "BET")])
    sequence.append(["X->X/R",
                     [("CHECK", "FLOP"), ("CHECK", "FLOP"), ("CHECK", "TURN"),
                      ("BET", "TURN"), ("RAISE", "TURN"), ("CALL", "TURN")],
                     ("CHECK", "BET")])
    sequence.append(["X->X",
                     [("CHECK", "FLOP"), ("CHECK", "FLOP"),
                      ("CHECK", "TURN"), ("CHECK", "TURN")],
                     ("CHECK", "BET")])
    run_out_analysis(sequence, board, enter_cards, "OOP")

    # lines for BU
    sequence = []
    sequence.append(["Overall",
                     [("CHECK", "FLOP")],
                     ("CHECK", "BET")])
    sequence.append(["B",
                     [("CHECK", "FLOP"), ("BET", "FLOP"),
                      ("CALL", "FLOP"), ("CHECK", "TURN")],
                     ("CHECK", "BET")])
    sequence.append(["X",
                     [("CHECK", "FLOP"), ("CHECK", "FLOP"), ("CHECK", "TURN")],
                     ("CHECK", "BET")])
    sequence.append(["B->X",
                     [("CHECK", "FLOP"), ("BET", "FLOP"), ("CALL", "FLOP"),
                      ("CHECK", "TURN"), ("CHECK", "TURN"), ("CHECK", "RIVER")],
                     ("CHECK", "BET")])
    sequence.append(["B->B",
                     [("CHECK", "FLOP"), ("BET", "FLOP"), ("CALL", "FLOP"),
                      ("CHECK", "TURN"), ("BET", "TURN"), ("CALL", "TURN"),
                      ("CHECK", "RIVER")],
                     ("CHECK", "BET")])
    sequence.append(["X->B/C",
                     [("CHECK", "FLOP"), ("CHECK", "FLOP"),
                      ("CHECK", "TURN"), ("BET", "TURN"),
                      ("RAISE", "TURN"), ("CALL", "TURN"),
                      ("CHECK", "RIVER")],
                     ("CHECK", "BET")])
    sequence.append(["X->X",
                     [("CHECK", "FLOP"), ("CHECK", "FLOP"), ("CHECK", "TURN"),
                      ("CHECK", "TURN"), ("CHECK", "RIVER")],
                     ("CHECK", "BET")])
    run_out_analysis(sequence, board, enter_cards, "IP")


def test_matrix_analysis(board, general_view=VIEW_TYPES[1], subview=VIEW_TYPES[2], enter_cards="", result_filename=DEFAULT_VIEW_RESULT_FILENAME):
    sequence = [("CHECK", "FLOP")]
    actions = ("CHECK", "BET")
    results = view_matrix(sequence, actions, board)
    # results = [*zip(*results)]
    org_print_result_matrix(results, result_filename)


def test():
    logger = logging.getLogger()
    logger.setLevel("DEBUG")
    board = "KdJh5h4c4s"
    board = "KdJh5h"
    sequence = [("CHECK", "FLOP")]
    # actions = ("CHECK", "BET")
    # default_view(sequence, actions, board)
    # sequence = [("CHECK", "FLOP"), ("BET", "FLOP")]
    # actions = ("FOLD", "CALL", "RAISE")
    # default_view(sequence, actions, board)
    # sequence = [("CHECK", "FLOP"), ("BET", "FLOP"),
    #             ("CALL", "FLOP"), ("CHECK", "TURN"), ("CHECK", "TURN")]
    actions = ("FOLD", "CALL", "RAISE")
    # actions = ("CHECK", "BET")
    sequence = [("CHECK", "FLOP"), ("BET", "FLOP"), ("CALL", "FLOP"),
                ("CHECK", "TURN"), ("BET", "TURN"), ("CALL", "TURN"),
                ("CHECK", "RIVER"), ("BET", "LAST")
                ]
    sequence = [("CHECK", "FLOP"), ("BET", "FLOP")]
    actions = ("FOLD", "CALL", "RAISE")

    current_view()
    # default_view(sequence, actions, board)
    # default_view(sequence, actions, board)
    # test_runout_analysis()
    # test_matrix_analysis(board)


if (__name__ == '__main__'):
    test()
