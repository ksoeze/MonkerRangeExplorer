#!/usr/bin/env python3

from monker_automation.utils import *
from monker_automation.gui import enter_sequence_and_save_ranges
from monker_automation.range import strategy_overview
from monker_automation.range import org_print_result_matrix
from monker_automation.views import get_view
from monker_automation.views import print_default_view


def default_view(sequence, actions, board, result_filename=DEFAULT_VIEW_RESULT_FILENAME):
    # generate view
    view = get_view(board, VIEW_TYPES[0])
    print_default_view(view)
    debug = enter_sequence_and_save_ranges(sequence, actions)
    print(debug)
    results = strategy_overview(actions, view)
    org_print_result_matrix(results, result_filename)


def test():
    board = "KdJh5h"
    board = "KdJh5h5c8h"
    sequence = [("CHECK", "FLOP"), ("BET", "FLOP"), ("CALL", "FLOP"),
                ("CHECK", "TURN"), ("BET", "TURN"), ("CALL", "TURN"),
                ("CHECK", "RIVER"), ("BET", "LAST")]
    actions = ("FOLD", "CALL", "ALLIN")
    default_view(sequence, actions, board)


if (__name__ == '__main__'):
    test()
