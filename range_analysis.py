#!/usr/bin/env python3
from monker_automation.gui import read_situation_and_save_ranges
from monker_automation.range_analysis_gui import start_gui
from monker_automation.utils import HAND_QUIZ, PREFLOP, RANGE_FOLDER, CARDS, MANUAL_SAVE_RANGES, \
    DEFAULT_REPORT_DIRECTORY,PLO5,PLO5_DIR,SUIT_COLORS,SUIT_SIGN_DIC
import  os
from tkinter import Tk
from PIL import Image, ImageDraw, ImageFont
import gzip
import shutil

def manual_hand_ranges():
    # without pyautogui...save ranges per hand to cvs and copy board into clipboard
    files = os.listdir(RANGE_FOLDER)
    files = [r for r in files if ".csv" in r]
    files = sorted(files, key=lambda x:os.path.getctime(os.path.join(RANGE_FOLDER,x)))

    if len(files) < 2:
        print("Found < 2 range files...please save ranges again")
        exit()
    if len(files) > 6:
        print("Too many range files...clear up the range folder")
        exit()
    actions = [r.replace(".csv","") for r in files]
    print("Found these actions:{}".format(actions))
    if PREFLOP:
        return actions,"2h2s2c2d"
    gui = Tk()
    board = gui.clipboard_get()
    gui.update()
    gui.destroy()
    board = ''.join(board.split())

    chunks, chunk_size = len(board), 2
    board_cards = [ board[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
    for card in board_cards:
        if card not in CARDS:
            print("Seems to be invalid board string in clipboard:")
            print(board)
            exit()
    print("Board seems to be: {}".format(board))
    return actions,board

def generate_table_image(line,board,spot):
    width = 591
    height = 474
    message = "SPOT: " + spot +"\n"
    message +="BOARD: "+ board +"\n"
    message +=line

    font = ImageFont.truetype("arial.ttf", size=40)

    img = Image.new('RGB', (width, height), color='white')

    imgDraw = ImageDraw.Draw(img)
    imgDraw.text((100,50), spot, font=font, fill="black")
    for i in range(0,6,2):
        card = board[i:i+2]
        color = SUIT_COLORS[card[1]]
        card = card[0]+SUIT_SIGN_DIC[card[1]]
        font = ImageFont.truetype("arial.ttf", size=100)
        imgDraw.text((100+i*60,150), card, font=font, fill=color)
    font = ImageFont.truetype("arial.ttf", size=30)
    imgDraw.text((60,350), line, font=font, fill="black")
    img.save(os.path.join(DEFAULT_REPORT_DIRECTORY,'table_plo5.png'))

def read_plo5_dir(hand_dir):
    gui = Tk()
    try:
        clipboard_string = gui.clipboard_get()
        gui.update()
        gui.destroy()
    except:
        clipboard_string = ""

    if PLO5_DIR[0:45] in clipboard_string:
        hand_dir = clipboard_string
    else:
        hand_dir = PLO5_DIR

    spot_components = hand_dir.split("/")
    line=spot_components[-2]
    board=spot_components[-3]
    spot=spot_components[-4]

    generate_table_image(line,board,spot)

    files = os.listdir(hand_dir)
    files = sorted(files, key=lambda x:os.path.getctime(os.path.join(hand_dir,x)))
    if len(files) < 2:
        print("Found < 2 range files...in Line directory: {}".format(hand_dir))
        exit()
    if len(files) > 6:
        print("Too many range files...in Line directory: {}".format(hand_dir))
        exit()
    actions = files
    print("Found these actions:{}".format(actions))
    board = ''.join(board.split())

    chunks, chunk_size = len(board), 2
    board_cards = [ board[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
    for card in board_cards:
        if card not in CARDS:
            print("Seems to be invalid board string:")
            print(board)
            exit()
    print("Board seems to be: {}".format(board))

    for file in files:
        input = os.path.join(hand_dir,file)
        output = os.path.join(RANGE_FOLDER,file+".csv")
        with gzip.open(input, 'rt') as f_in:
            with open(output, 'wt') as f_out:
                shutil.copyfileobj(f_in, f_out)
    return actions,board

if __name__ == '__main__':
    if not HAND_QUIZ:
        print("PLZ set HAND_QUIZ True to continue...exiting")
        exit()
    gui = Tk()
    try:
        clipboard_string = gui.clipboard_get()
    except:
        clipboard_string = ""
    gui.update()
    gui.destroy()
    if PLO5_DIR[0:45] in clipboard_string:
        actions, board = read_plo5_dir(clipboard_string)
        start_gui(actions,board)
    elif PLO5:
        actions, board = read_plo5_dir(PLO5_DIR)
        start_gui(actions,board)
    elif MANUAL_SAVE_RANGES:
        actions, board = manual_hand_ranges()
        start_gui(actions,board)
    else:
        infos = read_situation_and_save_ranges()
        board = infos["board"]
        actions = infos["actions"]
        start_gui(actions,board)