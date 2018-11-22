#!/usr/bin/env python3

from monker_automation.utils import *
import pyautogui
#import sys
import time
from tkinter import Tk


def goto_start(position=BACK_CO, click_delay=CLICK_DELAY, move_delay=MOUSE_MOVEMENT_DEL, num_back=NUM_BACK):
    move_click(position, move_delay, click_delay)
    for i in range(num_back):
        pyautogui.click()
        time.sleep(click_delay)
    return


def move_click(position, move_delay=MOUSE_MOVEMENT_DEL, click_delay=CLICK_DELAY):
    pyautogui.moveTo(position[0], position[1], move_delay)
    pyautogui.click()
    time.sleep(click_delay)


def copy_text(position, move_delay=MOUSE_MOVEMENT_DEL):
    pyautogui.moveTo(position[0], position[1], move_delay)
    pyautogui.click()
    pyautogui.hotkey('ctrl', 'a')  # mark everything
    pyautogui.hotkey('ctrl', 'c')
    return Tk().clipboard_get()


def write_board(position, text, move_delay=MOUSE_MOVEMENT_DEL, type_delay=TYPE_DELAY):
    pyautogui.moveTo(position[0], position[1], move_delay)
    pyautogui.click()
    for i in range(DELETE_BOARD):
        pyautogui.press('backspace')
        time.sleep(type_delay)
    pyautogui.typewrite(text, interval=type_delay)


def enter_sequence(sequence, reset=True, move_delay=MOUSE_MOVEMENT_DEL, click_delay=CLICK_DELAY):
    if reset:
        goto_start(BACK_CO, click_delay, move_delay, NUM_BACK)
    for item in sequence:
        if item[0] == "CHECK" or item[0] == "CALL":
            move_click(CHECK_CO, move_delay, click_delay)
        elif item[0] == "BET" or item[0] == "ALLIN" or item[0] == "RAISE":
            if item[1] == "LAST":
                move_click(CHECK_CO, move_delay, click_delay)
            else:
                move_click(BET_CO, move_delay, click_delay)


def save_range(position, filename, move_delay=MOUSE_MOVEMENT_DEL, click_delay=CLICK_DELAY, type_delay=TYPE_DELAY):
    move_click(position, move_delay, click_delay)
    pyautogui.typewrite(filename, interval=type_delay)
    move_click(SAVE_OK, move_delay, click_delay)
    time.sleep(SLEEP_AFTER_SAVE)


def save_ranges(actions, move_delay=MOUSE_MOVEMENT_DEL, click_delay=CLICK_DELAY):
    if len(actions) == 2:
        save_range(ACTION_1, actions[0], move_delay, click_delay)
        save_range(ACTION_3, actions[1], move_delay, click_delay)
    elif len(actions) == 3:
        save_range(ACTION_1, actions[0], move_delay, click_delay)
        save_range(ACTION_2, actions[1], move_delay, click_delay)
        save_range(ACTION_3, actions[2], move_delay, click_delay)
    else:
        print("ONLY 2 OR 3 ACTIONS SUPPORTED SO FAR")


def enter_sequence_and_save_ranges(sequence, actions, board=""):
    results = {}
    results["board"] = ""
    results["line"] = ""
    if len(actions) > 3:
        print("ONLY MAX 3 ACTIONS SUPPORTED (single betsize trees)")
        return results
    # enter board if given:
    if board != "":
        write_board(BOARD_CLICK, board)
    results = {}
    results["board"] = copy_text(BOARD_CLICK)
    # enter sequence
    enter_sequence(sequence)
    results["line"] = copy_text(LINE_CLICK)
    # save ranges
    save_ranges(actions)
    time.sleep(SLEEP_AFTER_FINISH)
    return results


def test():
    # mouse_coordinates()
    line_before = []
    sequence = [("CHECK", "FLOP")]
    actions = ("CHECK", "BET")

    # goto_start()
    # print(copy_text(BOARD_CLICK))
    # print(copy_text(LINE_CLICK))
    # write_board(BOARD_CLICK, "Kh Qs")
    # enter_sequence(sequence)
    # print(copy_text(LINE_CLICK))
    # save_ranges(actions)

    debug = enter_sequence_and_save_ranges(sequence, actions, "Ac Td")
    print("The BOARD is: {}".format(debug["board"]))
    print("The LINE is:\n {}".format(debug["line"]))


def mouse_coordinates():
    print('Press Ctrl-C to quit.')
    try:
        while True:
            x, y = pyautogui.position()
            positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print(positionStr, end='')
            print('\b' * len(positionStr), end='', flush=True)
    except KeyboardInterrupt:
        print('\n')


if (__name__ == '__main__'):
    mouse_coordinates()
    # test()
