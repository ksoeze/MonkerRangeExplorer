#!/usr/bin/env python3
import datetime
import subprocess

from PIL import Image

from monker_automation.utils import *
import pyautogui
import time
from tkinter import Tk
import os
import logging
import mss

import pyscreeze

pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False
#from timebudget import timebudget


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
    if HAND_QUIZ:
        move_click(ZERO_HANDS_SELECT, move_delay, click_delay)
    move_click(FILE_TEXT, move_delay, click_delay)
    if MONKER_BETA:
        filename+=".csv"
    pyautogui.typewrite(filename, interval=type_delay)
    move_click(SAVE_OK, move_delay, click_delay)
    time.sleep(SLEEP_AFTER_SAVE)
    if MONKER_BETA:
        move_click(MONKER_BETA_CLOSE_SAVE_RANGE,move_delay,click_delay)


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

#@timebudget
def available_buttons():
    buttons = {}

    # BACK is always on screen...take fixed coordinates

    tmp_screen = '.screenshot%s.png' % (datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))
    #subprocess.call(['scrot', tmp_screen])
    #tmp = Image.open(tmp_screen)

    try:
        sc = mss.mss().grab(mss.mss().monitors[0])
        tmp = Image.frombytes("RGB", sc.size, sc.bgra, "raw", "BGRX")
    except Exception as e:
        subprocess.call(['scrot', tmp_screen])
        tmp = Image.open(tmp_screen)

    buttons[BACK] = BACK_CO
    img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[CHECK])
    #coordinates = pyautogui.locateCenterOnScreen(img, region=CHECK_CALL_REGION,grayscale=True)

    coordinates = pyautogui.locate(img,tmp,region=CHECK_CALL_REGION,grayscale=True)
    if coordinates:
        coordinates = pyautogui.center(coordinates)
    #assert(coordinates == new_coordinates)

    buttons[CHECK] = coordinates
    if buttons[CHECK]:  # there cant be call option
        buttons[CALL] = None
    else:
        img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[CALL])
        #coordinates = pyautogui.locateCenterOnScreen(
        #    img, region=CHECK_CALL_REGION,grayscale=True)
        coordinates = pyautogui.locate(img,tmp,region=CHECK_CALL_REGION,grayscale=True)
        if coordinates:
            coordinates = pyautogui.center(coordinates)
        buttons[CALL] = coordinates

    buttons["BET"] = []
    last_action = copy_text(LINE_CLICK)
    last_action = last_action[-8:]
    is_bet = any([CALL in last_action, "FLOP" in last_action,
                  "TURN" in last_action, "RIVER" in last_action])
    #new monker beta the line field is empty so the last action string is still the board string ->
    #ugly hack ^^ 2.2023
    if not is_bet:
        if last_action[0:2] in CARDS:
            is_bet = True

    for size in POSSIBLE_BET_RAISE:
        img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[size])
        #coordinates = pyautogui.locateCenterOnScreen(img, region=BUTTON_REGION,grayscale=True)
        coordinates = pyautogui.locate(img,tmp,region=CHECK_CALL_REGION,grayscale=True)
        if coordinates:
            coordinates = pyautogui.center(coordinates)
        if coordinates:
            # last letters of line text -> call or flop, turn, river
            if is_bet:
                buttons["BET"].append(["BET " + size, coordinates])
            else:
                buttons["BET"].append(["RAISE " + size, coordinates])
        if len(buttons["BET"]) == MAX_BETS_RAISES:
            break
    if os.path.exists(tmp_screen):
        os.unlink(tmp_screen)
    return buttons

def available_buttons_literal():

    buttons = {}
    ranges = []
    # BACK is always on screen...take fixed coordinates

    tmp_screen = '.screenshot%s.png' % (datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))

    try:
        sc = mss.mss().grab(mss.mss().monitors[0])
        tmp = Image.frombytes("RGB", sc.size, sc.bgra, "raw", "BGRX")
    except Exception as e:
        subprocess.call(['scrot', tmp_screen])
        tmp = Image.open(tmp_screen)

    buttons[BACK] = BACK_CO

    img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[CHECK])
    coordinates = pyautogui.locate(img,tmp,region=BUTTON_REGION,grayscale=True)
    if coordinates:
        buttons[CHECK] = pyautogui.center(coordinates)
        ranges.append(CHECK)
    else:
        if CHECK in MISSING_RANGES:
            ranges.append(CHECK)

    img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[FOLD])
    coordinates = pyautogui.locate(img,tmp,region=BUTTON_REGION,grayscale=True)
    if coordinates:
        buttons[FOLD] = pyautogui.center(coordinates)
        ranges.append(FOLD)
    else:
        if FOLD in MISSING_RANGES or CALL in ranges:
            ranges.insert(0,FOLD)

    img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[CALL])
    coordinates = pyautogui.locate(img,tmp,region=BUTTON_REGION,grayscale=True)
    if coordinates:
        buttons[CALL] = pyautogui.center(coordinates)
        ranges.append(CALL)
    else:
        if CALL in MISSING_RANGES:
            ranges.append(CALL)

    buttons["BET"] = []

    if CHECK in ranges:
        bet_prefix = "BET "
    else:
        bet_prefix = "RAISE "

    for size in POSSIBLE_BET_RAISE:
        img = os.path.join(BUTTON_FILES_FOLDER, BUTTON_FILES[size])
        coordinates = pyautogui.locate(img,tmp,region=CHECK_CALL_REGION,grayscale=True)
        if coordinates:
            coordinates = pyautogui.center(coordinates)
            buttons["BET"].append([bet_prefix+size, coordinates])
            ranges.append(bet_prefix+size)
        if len(buttons["BET"]) == MAX_BETS_RAISES:
            break
#    if os.path.exists(tmp_screen):
#        os.unlink(tmp_screen)
    return buttons, ranges

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
    if PREFLOP:
        results["board"] = "2s2c2d2h"
    else:
        results["board"] = copy_text(BOARD_CLICK)
    results["line"] = copy_text(LINE_CLICK)

    if NEW_RANGE_DETECTION:
        buttons, actions = available_buttons_literal()
    else:
        buttons = available_buttons()
        actions = available_ranges(buttons)

    results["actions"] = actions
    results["button_coordinates"] = buttons

    file_name = os.path.join(DEFAULT_REPORT_DIRECTORY, TABLE_PNG_NAME)
    results["board_img"] = pyautogui.screenshot(region=BOARD_SCREEN_REGION)
    results["board_img"].save(file_name)

    file_name = os.path.join(DEFAULT_REPORT_DIRECTORY, RANGE_HEADER_PNG_NAME)
    results["range_img"] = pyautogui.screenshot(region=RANGE_SCREEN_REGION)
    results["range_img"].save(file_name)

    save_ranges(actions)
    return results


def update_board(start_board="", cards=[]):
    full_board = "".join([start_board]+cards)
    try:
        current_board = copy_text(BOARD_CLICK)
        current_board = current_board.replace(" ", "")
        if current_board == full_board:
            return
    except:
        logging.info("Empty board...trying to initialise")
        # TODO proper error handling...for now asume emtpy board

    move_click(BOARD_CLICK)
    for i in range(DELETE_BOARD):
        pyautogui.press('backspace')
        time.sleep(TYPE_DELAY)
    for card in cards:
        pyautogui.typewrite(" ", interval=TYPE_DELAY)
        pyautogui.typewrite(card, interval=TYPE_DELAY)
    if cards == []:
        pyautogui.typewrite(" ", interval=TYPE_DELAY)
    # choose check one time and go back in order to update ranges
    move_click(CHECK_CO)
    move_click(BACK_CO)
    current_board = copy_text(BOARD_CLICK)
    current_board = current_board.replace(" ", "")
    if current_board != full_board and start_board != "":
        logging.error("ERROR entering Board...exiting")
        exit()
    return current_board


def click_action(action, buttons):
    try:
        coordinates = buttons[action]
    except ValueError:
        logging.error("Impossible action in current Situation..exiting")
        exit()
    move_click(coordinates)


def click_back():
    move_click(BACK_CO)


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
