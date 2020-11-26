#!/usr/bin/env python3
from monker_automation.gui import read_situation_and_save_ranges
from monker_automation.range_analysis_gui import start_gui
from monker_automation.utils import HAND_QUIZ, PREFLOP
if __name__ == '__main__':
    if not HAND_QUIZ:
        print("PLZ set HAND_QUIZ True to continue...exiting")
        exit()
    infos = read_situation_and_save_ranges()
    board = infos["board"]
    actions = infos["actions"]
    start_gui(actions,board)