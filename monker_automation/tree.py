#!/usr/bin/env python3

from monker_automation.utils import *
from monker_automation.gui import update_board
from monker_automation.gui import click_action, click_back, goto_start
from monker_automation.gui import read_situation_and_save_ranges

from anytree import Node
import logging

_current_card_lvl = 0
_start_board = ""
_current_board = ""
_current_card_list = []
_infos = {}


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
    return bu_dic


def should_visit(action, action_results):
    return True


def add_subtrees(parent, line, cards_lvl1, cards_lvl2):
    logging.debug("LINE: {}".format(line))
    if not(line[-1] == CALL or line[-2:] == [CHECK, CHECK]):
        infos = read_situation_and_save_ranges()
        # view = get_view(infos["board"], VIEW_TYPES[0])  # fix this?
        buttons = convert_button_dic(infos["button_coordinates"])
        actions = infos["actions"]
        total_results, action_results = ([], [])
        #total_results, action_results = get_view_results(actions, view)
        node_name = "-".join(line)
        logging.debug(node_name)
        node = Node(node_name, parent=parent)  # , gui_info=infos,
        # overall_results=total_results, relativ_results=action_results)
        for button in buttons:
            if should_visit(button, action_results):
                click_action(button, buttons)
                line.append(button)
                add_subtrees(node, line, cards_lvl1, cards_lvl2)
                click_back()
                line = line[:-1]
    else:
        logging.debug("ADDING CARD TO LINE")
        global _current_card_lvl
        global _current_board
        global _current_card_list

        logging.debug("Current Card LVL: {}".format(_curre))

        if _current_card_lvl == 0:
            for card in cards_lvl1:
                if card in _current_board:  # invalid card
                    continue
                _current_card_lvl += 1
                _current_board += card
                _current_card_list.append(card)
                line.append(card)
                update_board(_start_board, _current_card_list)
                add_subtrees(parent, line, cards_lvl1, cards_lvl2)
                _current_card_lvl -= 1
                _current_board = _current_board[:-2]
                _current_card_list = _current_card_list[:-1]
                line = line[:-1]
        elif _current_card_lvl == 1:
            for card in cards_lvl2:
                if card in _current_board:  # invalid card
                    continue
                _current_card_lvl += 1
                _current_board += card
                _current_card_list.append(card)
                line.append(card)
                update_board(_start_board, _current_card_list)
                add_subtrees(parent, line, cards_lvl1, cards_lvl2)
                _current_card_lvl -= 1
                _current_board = _current_board[:-2]
                _current_card_list = _current_card_list[:-1]
                line = line[:-1]
    return


def walk_tree(turn_cards=[], river_cards=[]):
    #last_line = []
    current_line = []
    current_line.append(LINE_START)
    start_board = update_board()
    current_board = start_board
    _start_board = current_board
    _current_board = current_board
    current_board_list = [current_board[i:i+2]
                          for i in range(0, len(current_board), 2)]

    if turn_cards == [] and river_cards != []:
        cards_lvl1 = [
            card for card in river_cards if card not in current_board_list]
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

    add_subtrees(None, current_line, cards_lvl1, cards_lvl2)


def test():
    logger = logging.getLogger()
    logger.setLevel("DEBUG")
    turn_cards = ["4h"]
    river_cards = ["2d"]
    walk_tree(turn_cards, river_cards)


if (__name__ == '__main__'):
    test()
