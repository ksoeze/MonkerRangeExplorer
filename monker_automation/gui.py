#!/usr/bin/env python3

from monker_automation.utils import *
import pyautogui
#import sys
import time
from tkinter import Tk
import os
import logging


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
    gui = Tk()
    text = gui.clipboard_get()
    gui.destroy()
    return text


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
    move_click(CSV_SELECT, move_delay, click_delay)
    move_click(FILE_TEXT, move_delay, click_delay)
    pyautogui.typewrite(filename, interval=type_delay)
    move_click(SAVE_OK, move_delay, click_delay)
    time.sleep(SLEEP_AFTER_SAVE)


def save_ranges(actions, move_delay=MOUSE_MOVEMENT_DEL, click_delay=CLICK_DELAY):
    if len(actions) >= len(RANGE_CO) or len(actions) == 0:
        logging.error(
            "Save Range not possible because no actions or too many:")
        logging.error(actions)
        return
    co_list = RANGE_CO[len(actions)-1]
    for co, action in zip(co_list, actions):
        save_range(co, action, move_delay, click_delay)


def enter_sequence_and_save_ranges(sequence, actions, board=""):
    results = {}
    results["board"] = ""
    results["line"] = ""
    if len(actions) > 4:
        print("ONLY MAX 4 ACTIONS SUPPORTED (2 betsize trees)")
        print(actions)
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


def available_buttons():
    buttons = {}
    #img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[BACK])
    #coordinates = pyautogui.locateCenterOnScreen(img, region=BUTTON_REGION)

    # BACK is always on screen...take fixed coordinates
    buttons[BACK] = BACK_CO
    img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[CHECK])
    coordinates = pyautogui.locateCenterOnScreen(img, region=CHECK_CALL_REGION)
    buttons[CHECK] = coordinates
    if buttons[CHECK]:  # there cant be call option
        buttons[CALL] = None
    else:
        img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[CALL])
        coordinates = pyautogui.locateCenterOnScreen(
            img, region=CHECK_CALL_REGION)
        buttons[CALL] = coordinates

    buttons["BET"] = []
    last_action = copy_text(LINE_CLICK)
    last_action = last_action[-8:]
    is_bet = any([CALL in last_action, "FLOP" in last_action,
                  "TURN" in last_action, "RIVER" in last_action])
    print(last_action)
    print(is_bet)

    for size in POSSIBLE_BET_RAISE:
        img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[size])
        coordinates = pyautogui.locateCenterOnScreen(img, region=BUTTON_REGION)
        if coordinates:
            # last letters of line text -> call or flop, turn, river
            if is_bet:
                buttons["BET"].append(["BET " + size, coordinates])
            else:
                buttons["BET"].append(["RAISE " + size, coordinates])
        if len(buttons["BET"]) == MAX_BETS_RAISES:
            break
    # for item in buttons:
    #    print("{}: {}".format(item, buttons[item]))
    return buttons

# returns list of available ranges based on
# currently shown buttons and line window last action


def available_ranges(buttons):
    ranges = []
    if buttons["BET"] == [] and buttons[CHECK]:  # no betting option
        ranges.append(CHECK)
    elif buttons["BET"] == []:
        # guess facing AI
        ranges.append(FOLD)
        ranges.append(CALL)
    elif "BET" in buttons["BET"][0][0]:  # guess facing no bet
        ranges.append(CHECK)
        for bet in buttons["BET"]:
            ranges.append(bet[0])
    else:  # guess facing bet
        ranges.append(FOLD)
        ranges.append(CALL)
        for bet in buttons["BET"]:
            ranges.append(bet[0])
    return ranges


def read_situation_and_save_ranges():
    results = {}
    results["board"] = copy_text(BOARD_CLICK)
    results["line"] = copy_text(LINE_CLICK)

    buttons = available_buttons()
    actions = available_ranges(buttons)

    results["actions"] = actions
    results["button_coordinates"] = buttons

    save_ranges(actions)
    return results


def test():
    mouse_coordinates()
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
    #cProfile.run('test()', sort='cumtime')
    buttons = available_buttons()
    available_ranges(buttons)
    # debug = enter_sequence_and_save_ranges(sequence, actions, "Ac Td")
    # print("The BOARD is: {}".format(debug["board"]))
    # print("The LINE is:\n {}".format(debug["line"]))


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
