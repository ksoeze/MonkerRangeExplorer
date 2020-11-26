#!/usr/bin/env python3

from monker_automation.utils import *
from monker_automation.gui import update_board
from monker_automation.gui import click_action, click_back, goto_start
from monker_automation.gui import read_situation_and_save_ranges
from monker_automation.views import get_view
from monker_automation.range import get_view_results
from monker_automation.pdf_print import print_pdf, add_analysis_to_report, print_all_views, move_analysis_to_report_folder,combine_views_to_report
from monker_automation.plot import plot_default, plot_range_distribution
from anytree import Node, RenderTree
import logging
import pyautogui

_current_card_lvl = 0
_start_board = ""
_current_board = ""
_current_card_list = []
_infos = {}
_line = []
_line_list = []
_invalid_sequences = []

# TODO change available buttons in gui.py to make this unessasay
# or move it there...


def convert_button_dic(buttons):
    bu_dic = {}
    if buttons[CHECK]:
        bu_dic[CHECK] = buttons[CHECK]
    if buttons[CALL]:
        bu_dic[CALL] = buttons[CALL]
    for bet in buttons["BET"]:
        bu_dic[bet[0]] = bet[1]
    # print(bu_dic)
    return bu_dic


def valid_line():
    if _line_list == []:
        return True  # if no lines given all lines are valid
    for line in _line_list:
        is_valid_line = True
        if len(line) != len(_line):
            is_valid_line = False
        else:
            for tested_action, current_action in zip(line, _line):
                if CHECK in tested_action or CALL in tested_action or "BET" in tested_action or "RAISE" in tested_action:
                    if tested_action not in current_action:
                        is_valid_line = False
        if is_valid_line:
            return True
    return False


def skip_path():
    # invalid sequences is stronger bind than valide line list
    if _invalid_sequences != []:
        if len(_line) < 2:
            return False
        else:
            for sequence in _invalid_sequences:
                if sequence[0] in _line[-2] and sequence[1] in _line[-1]:
                    return True
        return False

    if _line_list == []:
        return False
    line_list_long = []
    skip_path = True
    for line in _line_list:
        if len(line) >= len(_line):
            line_list_long.append(line)
            skip_path = False
    if skip_path:
        return True
    # print(line_list_long)
    for i in range(len(_line)):
        if CHECK in _line[i] or CALL in _line[i] or "BET" in _line[i] or "RAISE" in _line[i]:
            if all([line[i] not in _line[i] for line in line_list_long]):
                return True
    return False


def should_visit(action, action_results):
    if "RAISE" in action:
        total_value = action_results[action]["p"][0]
        if total_value < MIN_RAISE_FREQ:
            return False
        else:
            return True
    else:
        total_value = action_results[action]["p"][0]
        if total_value < MIN_FREQ:
            return False
        else:
            return True


def print_infos(node_name, total_results, action_results, infos, report_name):
    plot_default(total_results, action_results, infos["actions"])
    plot_range_distribution(total_results, action_results, infos["actions"])
    print_pdf(_line)
    #add_analysis_to_report(report_name, _start_board + "-".join(_line))
    move_analysis_to_report_folder(report_name, _start_board + "-".join(_line))
    # TODO add infos to dictionary and save results at the end?


def add_subtrees(parent, cards_lvl1, cards_lvl2):
    global _line
    global _current_board
    # only parse lines which are of interest

    if not(_line[-1] == CALL or _line[-2:] == [CHECK, CHECK]):
        infos = read_situation_and_save_ranges()
        view = get_view(_current_board, SCRIPT_VIEW_TYPE[0])
        buttons = convert_button_dic(infos["button_coordinates"])
        actions = infos["actions"]

        node_name = _line[-1]
        node = Node(node_name, parent=parent)  # , gui_info=infos,
        # overall_results=total_results, relativ_results=action_results)
        # total_results, action_results = ([], [])
        total_results, action_results = get_view_results(actions, view)
        logging.info("adding node of LINE: {}".format(_line))
        logging.info("current board is: {}".format(_current_board))

        if valid_line():
            logging.info("VALID LINE: {}".format(_line))
            print_infos(node_name, total_results, action_results, infos,_start_board+"-"+SCRIPT_VIEW_TYPE[0])
            for view_type in SCRIPT_VIEW_TYPE[1:]:
                view = get_view(_current_board, view_type)
                total_results, action_results = get_view_results(actions, view)
                print_infos(node_name, total_results, action_results, infos,_start_board+"-"+view_type)
        for button in buttons:
            if should_visit(button, action_results):
                _line.append(button)
                logging.info("Increased LINE: {}".format(_line))
                if not skip_path():
                    click_action(button, buttons)
                    add_subtrees(node, cards_lvl1, cards_lvl2)
                    click_back()
                else:
                    logging.info("Skip PATH: {}".format(_line))
                _line = _line[:-1]
                logging.info("Decreased LINE: {}".format(_line))
    else:
        logging.info("ADDING CARD TO LINE")
        global _current_card_lvl
        global _current_card_list

        if _current_card_lvl == 0:
            for card in cards_lvl1:
                if card in _current_board:  # invalid card
                    continue
                _current_card_lvl += 1
                _current_board += card
                _current_card_list.append(card)
                _line.append(card)
                update_board(_start_board, _current_card_list)
                add_subtrees(parent, cards_lvl1, cards_lvl2)
                _current_card_lvl -= 1
                _current_board = _current_board[:-2]
                _current_card_list = _current_card_list[:-1]
                _line = _line[:-1]
        elif _current_card_lvl == 1:
            for card in cards_lvl2:
                if card in _current_board:  # invalid card
                    continue
                _current_card_lvl += 1
                _current_board += card
                _current_card_list.append(card)
                _line.append(card)
                update_board(_start_board, _current_card_list)
                add_subtrees(parent, cards_lvl1, cards_lvl2)
                _current_card_lvl -= 1
                _current_board = _current_board[:-2]
                _current_card_list = _current_card_list[:-1]
                _line = _line[:-1]
    if _line == [LINE_START]:
        return node
    else:
        return


def walk_tree(valid_lines=[], invalid_sequences=[], turn_cards=[], river_cards=[]):
    global _line
    global _start_board
    global _current_board
    global _line_list
    global _invalid_sequences

    # last_line = []
    _line.append(LINE_START)
    goto_start()
    start_board = update_board()
    _start_board = start_board
    _current_board = start_board
    _line_list = valid_lines
    _invalid_sequences = invalid_sequences

    current_board_list = [_current_board[i:i+2]
                          for i in range(0, len(_current_board), 2)]

    if turn_cards == [] and river_cards != []:
        cards_lvl1 = [
            card for card in river_cards if card not in current_board_list]
        cards_lvl2 = []
    elif turn_cards != [] and river_cards == []:
        cards_lvl1 = [
            card for card in turn_cards if card not in current_board_list]
        cards_lvl2 = []
    elif turn_cards == [] and river_cards == []:
        cards_lvl1 = []
        cards_lvl2 = []
    elif turn_cards != [] and river_cards != []:
        cards_lvl1 = [
            card for card in turn_cards if card not in current_board_list]
        cards_lvl2 = [
            card for card in river_cards if card not in current_board_list]
    else:
        logging.error("Invalid combo of turn and or rivercards")
        exit()

    root = add_subtrees(None, cards_lvl1, cards_lvl2)
    board=_current_board
    # board="Qd3d2d Ks"CALL
    for view in SCRIPT_VIEW_TYPE:
        combine_views_to_report(board+"-"+view)
    if PRINT_VIEWS:
        print_all_views(board)
        if cards_lvl1:
            for item in cards_lvl1:
                print_all_views(board+" "+item)
        if cards_lvl2:
            for turn in cards_lvl1:
                for river in cards_lvl2:
                    print_all_views(board+" "+turn+" "+river)

    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))


def start_walker():
    logger = logging.getLogger()
    logger.setLevel("INFO")
    turn_cards = TURN_CARDS
    river_cards =  RIVER_CARDS
    invalid_sequences = INVALID_SEQUENCES
    valid_lines = VALID_LINES
    if HAND_QUIZ:
        logger.error("Plz set HAND_QUIZ to false...exiting")
        exit()
    if NEW_RANGE_DETECTION:
         logger.error("Plz set NEW_RANGE_DETECTION to false...exiting")
         exit()

    walk_tree(valid_lines, invalid_sequences, turn_cards, river_cards)


if (__name__ == '__main__'):
    start_walker()
    if SHUTDOWN:
        import subprocess
        subprocess.call("systemctl poweroff",shell=True)
    else:
        pyautogui.hotkey('ctrl', 'alt', 'delete')
