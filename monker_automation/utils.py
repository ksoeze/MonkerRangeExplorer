#!/usr/bin/env python

# default True - when False the script tries to use the automatic range saving from the monker gui
# this requires extra setup steps (save reference images of buttons, setup pyautogui, exact positioning of the monker window etc)
MANUAL_SAVE_RANGES=True
# Only relevant when using the automatic ranges saving stuff 
# Monker 1 and Monker 2 have different graphics and positioning 
MONKER_BETA = True

# Private PLO 5-Card spots 
PLO5_DIR="/home/johann/monker-beta/ranges/Omaha5/Postflop/SRP-EP-BTN/Js8c2h/BET75-/"
PLO5 = False

## ------------------------------------------------------------------------------------------------------------------------------
## ** ALL Settings for range retrieval on different devices - not nessasary with manual range saving 

Y_OFFSET= 0 #845 # 827 #865

LAPTOP=True
# xdotool getwindowgeometry 113246246
# Window 113246246
#  Position: 1932,2031 (screen: 0)
#  Geometry: 1908x1011
# thats the reference value
# positioning seems to be:
# x-12 and y-48 (on the 4k display)
# xdotool windowsize 113246246 1908 1011
# xdotool windowmove 113246246 1920 1945

# xdotool windowmove values are:
# so X = 1932-10-X_LAPTOP_OFFSET
#    Y = 1186-42-Y_LAPTOP_OFFSET

if LAPTOP:
    X_LAPTOP_OFFSET = -1700
    Y_LAPTOP_OFFSET = -1000
else:
    Y_LAPTOP_OFFSET = 0
    X_LAPTOP_OFFSET = 0

# --------------------------------------------------------------------------------------------------------------    
# poker constants

RANKS = list("AKQJT98765432")
SUITS = list("cdhs")
CARDS = list(rank + suit for suit in SUITS for rank in RANKS)
RANDOM_RANKS = list("RON")
RANDOM_SUITS = list("wxyz")
RANDOM_CARD = 'Bb'
RANDOM_CARDS = list(
    rank + suit for suit in RANDOM_SUITS for rank in RANDOM_RANKS)
RANDOM_BOARD = [RANDOM_CARD] * 5
RANK_ORDER = {'A': 12, 'K': 11, 'Q': 10, 'J': 9, 'T': 8, '9': 7,
              '8': 6, '7': 5, '6': 4, '5': 3, '4': 2, '3': 1, '2': 0}
LOW_RANK_ORDER = {'K': 12, 'Q': 11, 'J': 10, 'T': 9, '9': 8,
                  '8': 7, '7': 6, '6': 5, '5': 4, '4': 3, '3': 2, '2': 1, 'A': 0}
LOW_CARDS = list("A2345678")
STRAIGHTS = [list("AKQJT"), list("KQJT9"), list("QJT98"), list("JT987"), list(
    "T9876"), list("98765"), list("87654"), list("76543"), list("65432"), list("5432A")]
INVALID_CHAR = '#'

# view constants
# These variables define how many hands are grouped to one cathegory 
# For exable FD_GROUPING = [ 1,2,2] means flushdraws are bucketed like this 
# [NDF], [2nd NDF, 3rd NDF], [4st NDF, 5st NDF], [all other lower flushdraws]
# did not change things a long time but might be usefull for powerusers to get more or less grained cathegory in the overviews
# you have to be carefull not to make too many buckets because at some point the overview doesnt fit properly anymore and you get 
# bad graphics / overlapping / nonreadable legends

QUAD_BOARD_PAIR_GROUPING = [1, 1, 2, 2, 3]
PAIRED_BOARD_FULL_OR_BETTER_GROUPING = [2, 2]
FLUSH_GROUPING = [1, 1, 2,2]
OVERPAIR_GROUPING = [1, 2]
FD_GROUPING = [1, 2,2]
FD_BLOCKER_GROUPING = [1,3]
BD_FD_GROUPING = [1]
STR_DRAW_GROUPING = [3,3]
SET_GROUPING = [1, 1]
PAIR_GROUPING = [1, 1]
POCKET_PAIR_GROUPING = [1,1,1,1,1,1,2,2,2,2]
MIDDLE_PAIR_GROUPING = [2]
BOARD_INTERACTION_GROUPING = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
VIEW_TYPES = ["DEFAULT", "MADE_HANDS", "DRAWS", "BLOCKERS", "DRAWS_BLOCKERS", "FLUSH","STRAIGHT",
    "BOARD_RANKS", "KEY_CARDS","POCKET_PAIRS","CUSTOM"]

# if you want to use the different views directly in monker put the path to the monkerinstallation/Views folder here.
# to use this feature put PRINT_VIEWS = True in line 392
VIEW_FOLDER = "/media/johann/MONKER/monker/Views/"
DEFAULT_VIEW_NAME = "OVERVIEW"
TOP_VIEW_LINE = "180\n"
MIN_WEIGHT = 0.001 #0.001

# custom views
# range constants
# here put the ranges directory where you save your exported ranges 
# can be the default ranges folder of monker or somewhere else
# ATTENTION: the script deletes the exportet .cvs ranges after usage since only the ranges for the current spot should be in there 
# additional folders like preflop ranges etc in this folder are ok and are not touched

if MONKER_BETA:
    RANGE_FOLDER = "./ranges/" #/home/johann/monker-beta/ranges/"
else:
    RANGE_FOLDER = "./ranges/" #/home/johann/monker-1/ranges/"

# gui reader constants
# here all the positioning of the monker buttons etc are set 
# not relevant for manual range saving 
# it changed over the years for different monitor setups / screen resolutions / devices but overall quite straight forward
# if you really wanna use it and have looked through the code a bit but cant figure it out - feel free to file a github issue and I might help out
 
BACK_CO = (3885+X_LAPTOP_OFFSET, 923+Y_LAPTOP_OFFSET)
BACK_CO = (1952+X_LAPTOP_OFFSET, 2025+Y_OFFSET+Y_LAPTOP_OFFSET)
CHECK_CO = (3955+X_LAPTOP_OFFSET, 925+Y_LAPTOP_OFFSET)
CHECK_CO = (1997+X_LAPTOP_OFFSET, 2025+Y_OFFSET+Y_LAPTOP_OFFSET)
BET_CO = (4039+X_LAPTOP_OFFSET, 925+Y_LAPTOP_OFFSET)
BET_CO = (2047+X_LAPTOP_OFFSET, 2025+Y_OFFSET+Y_LAPTOP_OFFSET)


# BUTTONS_CO = [(3955, 925), (4039, 925), (4123, 925), (4200, 925)]
if MONKER_BETA:
    BOARD_CLICK = (4000+X_LAPTOP_OFFSET, 250+Y_LAPTOP_OFFSET)  # monker beta
    BOARD_CLICK = (2144+X_LAPTOP_OFFSET, 1354+Y_OFFSET+Y_LAPTOP_OFFSET)
else:
    BOARD_CLICK = (4000+X_LAPTOP_OFFSET, 255+Y_LAPTOP_OFFSET)
    BOARD_CLICK = (2144+X_LAPTOP_OFFSET, 1359+Y_OFFSET+Y_LAPTOP_OFFSET)
    BOARD_CLICK = (2144+X_LAPTOP_OFFSET, 1369+Y_OFFSET+Y_LAPTOP_OFFSET)
#
LINE_CLICK = (4040+X_LAPTOP_OFFSET, 1000+Y_LAPTOP_OFFSET)
LINE_CLICK = (2205+X_LAPTOP_OFFSET, 2124+Y_OFFSET+Y_LAPTOP_OFFSET)
# index 0 is for 1 range; index 2 for 2 ranges etc

RANGE_CO = [[(4400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET)],
            [(4400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (5400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET)],
            [(4400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (4900+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (5400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET)],
            [(4400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (4750+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (5050+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (5400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET)],
            [(4400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (4650+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (4920+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (5150+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (5400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET)],
            [(4400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (4600+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (4820+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET),
             (5000+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (5200+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET), (5400+X_LAPTOP_OFFSET, 95+Y_OFFSET+Y_LAPTOP_OFFSET)],
            ]
RANGE_CO = [[(2410+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET)],
            [(2410+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (3691+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET)],
            [(2410+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (3045+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (3691+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET)],
            [(2410+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (2889+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (3286+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (3681+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET)],
            [(2410+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (2761+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (3090+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (3362+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (3691+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET)],
            [(2410+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (2685+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (2952+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET),
             (3189+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (3454+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET), (3717+X_LAPTOP_OFFSET, 1200+Y_OFFSET+Y_LAPTOP_OFFSET)],
            ]

SAVE_OK = (4648+X_LAPTOP_OFFSET, 637+Y_LAPTOP_OFFSET)
if MONKER_BETA:
    SAVE_OK = (3030+X_LAPTOP_OFFSET, 1794+Y_OFFSET+Y_LAPTOP_OFFSET)#(2842, 1751)
else:
    SAVE_OK = (2842+X_LAPTOP_OFFSET, 1749+Y_OFFSET+Y_LAPTOP_OFFSET)#(2842, 1751)
CSV_SELECT = (4577, 534)
if MONKER_BETA:
    CSV_SELECT = (2936+X_LAPTOP_OFFSET, 1587+Y_OFFSET+Y_LAPTOP_OFFSET)#(2767, 1632)
else:
    CSV_SELECT = (2767+X_LAPTOP_OFFSET, 1630+Y_OFFSET+Y_LAPTOP_OFFSET)#(2767, 1632)
FILE_TEXT = (4592, 602)
if MONKER_BETA:
    FILE_TEXT = (2945+X_LAPTOP_OFFSET, 1837+Y_OFFSET+Y_LAPTOP_OFFSET)
else:
    FILE_TEXT = (2817+X_LAPTOP_OFFSET, 1713+Y_OFFSET+Y_LAPTOP_OFFSET)
ZERO_HANDS_SELECT = (4664, 575)
if MONKER_BETA:
    ZERO_HANDS_SELECT = (2951+X_LAPTOP_OFFSET, 1653+Y_OFFSET+Y_LAPTOP_OFFSET)
else:
    ZERO_HANDS_SELECT = (2847+X_LAPTOP_OFFSET, 1679+Y_OFFSET+Y_LAPTOP_OFFSET)
MONKER_BETA_CLOSE_SAVE_RANGE = (3069+X_LAPTOP_OFFSET, 1444+Y_OFFSET+Y_LAPTOP_OFFSET)
FILTER_Y_OFFSET = 10

BOARD_SCREEN_REGION = (3842, 578, 450, 450)
BOARD_SCREEN_REGION = (1929+X_LAPTOP_OFFSET, 1677+Y_OFFSET+Y_LAPTOP_OFFSET, 450, 450)
RANGE_SCREEN_REGION = (4298, 2, 1185, 98)
RANGE_SCREEN_REGION = (2292+X_LAPTOP_OFFSET, 1185+Y_OFFSET+Y_LAPTOP_OFFSET, 1518, 70)
FILTER_SCREEN_REGION = (4963,967,500,80)
FILTER_SCREEN_REGION = (2720+X_LAPTOP_OFFSET,2091+Y_OFFSET+Y_LAPTOP_OFFSET,340,25)



NUM_BACK = 10
DELETE_BOARD = 7
MOUSE_MOVEMENT_DEL = 0.1
CLICK_DELAY = 0.1
TYPE_DELAY = 0.01
SLEEP_AFTER_SAVE = 0.5
SLEEP_AFTER_FINISH = 1

FOLD = "FOLD"
BACK = "BACK"
CHECK = "CHECK"
CALL = "CALL"
BET = "BET"
RAISE = "RAISE"
BUTTON_FILES = {"CHECK": "check.png", "FOLD": "fold.png", "CALL": "call.png", "MIN": "min.png",
                "10": "10.png", "15": "15.png", "20": "20.png", "25": "25.png", "30": "30.png", "33": "33.png",
                "35": "35.png", "40": "40.png", "50": "50.png", "55":"55.png","60": "60.png",
                "66": "66.png", "70": "70.png", "75": "75.png", "80": "80.png",
                "90": "90.png", "100": "100.png", "AllIn": "allin.png"}
if MONKER_BETA:
    if LAPTOP:
        BUTTON_FILES_FOLDER = "/home/johann/code/monker_automation/monker_automation/buttons-beta-lap/"
    else:
        BUTTON_FILES_FOLDER = "/home/johann/code/monker_automation/monker_automation/buttons-beta-4k/"
else:
    if LAPTOP:
        BUTTON_FILES_FOLDER = "/home/johann/code/monker_automation/monker_automation/buttons-lap/"
    else:
        BUTTON_FILES_FOLDER = "/home/johann/code/monker_automation/monker_automation/buttons-4k/"     
BUTTON_REGION = (3880, 915, 4200, 931) #(3940, 915, 4200, 931)
BUTTON_REGION = (1932, 2018+Y_OFFSET, 2277, 2044+Y_OFFSET)
BUTTON_REGION = (1932+X_LAPTOP_OFFSET, 2018+Y_OFFSET+Y_LAPTOP_OFFSET, 350, 30)
CHECK_CALL_REGION = (3880, 915, 4000, 931) #(3940, 915, 4000, 931)  # restrict for performance reasons
CHECK_CALL_REGION = (1932, 2018+Y_OFFSET, 2277, 2044+Y_OFFSET)
CHECK_CALL_REGION = (1932+X_LAPTOP_OFFSET, 2018+Y_OFFSET+Y_LAPTOP_OFFSET, 350, 30)

# info tree creation
# these constants are for the old pdf report generation tool 
# I dont use it anymore since I prefere the much more rich matrix view + quiz 
# It used to "walk" through monker trees automatically and generate a pdf report of all main spots 
# only works when you have setup all auto range saving stuff correctly
LINE_START = "|"

# standard lines

# 1 bet lines
CARD_DUMMY = ["Ah"]
OOP_BET = [LINE_START, ]
IP_BET = [LINE_START, CHECK]
OOP_X_BET = IP_BET + [CHECK] + CARD_DUMMY
IP_X_BET = OOP_X_BET + [CHECK]
OOP_X_X_BET = IP_X_BET + [CHECK] + CARD_DUMMY
IP_X_X_BET = OOP_X_X_BET + [CHECK]

# 2nd and 3rd barrel of IP and action vs bet
OOP_vsBET = [LINE_START, CHECK, BET]
IP_BET_BET = OOP_vsBET + [CALL] + CARD_DUMMY + [CHECK]
OOP_CALL_vsBET = IP_BET_BET + [BET]
IP_BET_BET_BET = OOP_CALL_vsBET + [CALL] + CARD_DUMMY + [CHECK]
OOP_CALL_CALL_vsBET = IP_BET_BET_BET + [BET]

# 2nd and 3rd barrel of OOP and action vs bet
IP_vsBET = [LINE_START, BET]
OOP_BET_BET = IP_vsBET + [CALL] + CARD_DUMMY
IP_CALL_vsBET = OOP_BET_BET + [BET]
OOP_BET_BET_BET = IP_CALL_vsBET + [CALL] + CARD_DUMMY
IP_CALL_CALL_vsBET = OOP_BET_BET_BET + [BET]

# one bet and face raise
IP_BET_vsRAISE = IP_BET + [BET] + [RAISE]
OOP_BET_vsRAISE = OOP_BET + [BET] + [RAISE]
IP_X_BET_vsRAISE = IP_X_BET + [BET] + [RAISE]
OOP_X_BET_vsRAISE = OOP_X_BET + [BET] + [RAISE]
IP_X_X_BET_vsRAISE = IP_X_X_BET + [BET] + [RAISE]
OOP_X_X_BET_vsRAISE = OOP_X_X_BET + [BET] + [RAISE]

# raise bet and action on next card
OOP_vsRAISE_BET = OOP_BET_vsRAISE + [CALL] + CARD_DUMMY
IP_RAISE_BET = OOP_vsRAISE_BET + [CHECK]
OOP_RAISE_BET = IP_BET_vsRAISE + [CALL] + CARD_DUMMY
IP_vsRAISE_BET = OOP_RAISE_BET + [CHECK]

# vs delay bet
IP_X_vsBET = OOP_X_BET + [BET]
OOP_X_vsBET = IP_X_BET + [BET]
IP_X_X_vsBET = OOP_X_X_BET + [BET]
OOP_X_X_vsBET = IP_X_X_BET + [BET]

# call once and then bet / donk
IP_CALL_BET = OOP_BET_BET + [CHECK]
OOP_BET_vsBET = IP_CALL_BET + [BET]
OOP_CALL_BET = OOP_vsBET + [CALL] + CARD_DUMMY
IP_BET_vsBET = OOP_CALL_BET + [BET]

# call once check and then bet / vs bet
IP_CALL_X_BET = IP_CALL_BET + [CHECK] + CARD_DUMMY + [CHECK]
OOP_CALL_X_BET = OOP_CALL_BET + [CHECK, CHECK] + CARD_DUMMY
IP_CALL_X_vsBET = OOP_CALL_X_BET + [BET]
OOP_CALL_X_vsBET = IP_CALL_X_BET + [BET]

# bet check bet
IP_BET_X_BET = OOP_CALL_X_BET + [CHECK]
OOP_BET_X_BET = IP_CALL_BET + [CHECK] + CARD_DUMMY
IP_BET_X_vsBET = OOP_CALL_X_BET + [BET]
OOP_BET_X_vsBET = IP_CALL_X_BET + [CHECK] + CARD_DUMMY + [CHECK] + [BET]

# call call bet
OOP_CALL_CALL_BET = OOP_CALL_vsBET + [CALL] + CARD_DUMMY
# analysis

DEFAULT_VIEW_RESULT_FILENAME = "/home/johann/code/monker_automation/RESULTS.org"
DEFAULT_REPORT_DIRECTORY = "./report"
DEFAULT_REPORT_VIEW_DIR = "/home/johann/Documents/poker/monker-documentation/MonkerReports/views/"
DEFAULT_REPORT_MATCHER_DIRECTORY = "/home/johann/Documents/poker/monker-documentation/MonkerReports/matcher/"
STRATEGY_PNG_NAME = "strat.png"
RANGE_PNG_NAME = "range.png"
VIEW_PDF_NAME = "view.pdf"
FILTER_PNG_NAME="filter.png"
# STRATEGY_PDF_NAME = "strategy.pdf"
REPORT_PDF_NAME = "report.pdf"
TABLE_PNG_NAME = "table.png"
TABLE_PNG_NAME_DUMMY = "table_dummy.png"
RANGE_HEADER_PNG_NAME = "range_header.png"
PICKLE_INFOS = "spot_infos"
EV_CVS = "hand_ev.cvs"
DEFAULT_BOOKMARK = "NO DESCRIPTION"

INFO_FONT = ("Helvetica", 22)
BUTTON_FONT = ("Helvetica", 14)
RESULT_FONT = ("Helvetica", 14)

SUIT_COLORS = {"h": "red", "d": "blue",
               "c": "green", "s": "black"}
SUIT_SIGN_DIC = {"h": "\u2665", "c": "\u2663", "s": "\u2660", "d": "\u2666"}

ANALYSIS_FONT = ("Arial", 12)
MAX_LABEL_LENGTH = 20

# SCRIPT SETTINGS

# View AUSWAHL = ["DEFAULT", "MADE_HANDS", "DRAWS", "BLOCKERS", "DRAWS_BLOCKERS", "CUSTOM"]
SCRIPT_VIEW_TYPE = ["DEFAULT", "MADE_HANDS"]
# SCRIPT_VIEW_TYPE = ["DEFAULT","MADE_HANDS", "DRAWS", "BLOCKERS", "DRAWS_BLOCKERS"]
# SCRIPT_VIEW_TYPE = ["DEFAULT","MADE_HANDS","BLOCKERS"]

# low blank, medium to high 2 fd card, A (or next non pairing card) "blank",
# top card pairing, bottom card paring, main oesd low card, gs card high card,
# flush blank, flush pairing (top or 2nd card paring), A (nf card) flush

# TURN_CARDS = ["2h","Ks","Ah","Qh","7h","9h","Jh","5d","Qd","Ad"]
TURN_CARDS = []
# RIVER_CARDS = ["Ac","Ks","Kc","Qh","Qd","Jc","Tc","9d","7c","6c","6d"]
RIVER_CARDS = ["6d"]
# z.b. [[RAISE,RAISE]] für bet, vs bet und vs raise lines only
INVALID_SEQUENCES = [[BET, RAISE]]
INVALID_SEQUENCES = [[RAISE, RAISE]]
#INVALID_SEQUENCES = []

# see lines.txt
VALID_LINES = [
    OOP_BET, IP_BET,
    OOP_BET_BET, IP_BET_BET,
    OOP_X_BET, IP_X_BET,
    IP_vsBET, OOP_vsBET,
    IP_X_vsBET, OOP_X_vsBET,
    IP_CALL_BET, OOP_CALL_BET,
    IP_BET_vsRAISE, OOP_BET_vsRAISE,
    IP_CALL_vsBET, OOP_CALL_vsBET,
    IP_X_BET_vsRAISE, OOP_X_BET_vsRAISE,
    IP_RAISE_BET, OOP_RAISE_BET,
    IP_vsRAISE_BET, OOP_vsRAISE_BET
]
VALID_LINES = []
# auswahl: ["10","20","25","30","35","40","50","60","66","70","75","80","100","AllIn"]
#POSSIBLE_BET_RAISE = ["50","100", "AllIn"]
POSSIBLE_BET_RAISE = ["MIN","10","20","25","30","33","40","50","55","60","66","70","75","100","AllIn"]

MAX_BETS_RAISES = 4
QUIZ = False
PRINT_VIEWS = False

MIN_FREQ = 10
MIN_RAISE_FREQ = 5

# Shutsdown Computer if not needed after finishing the job // locks screen otherwise
SHUTDOWN = False
#SHUTDOWN = True

# NEW RANGE DETECTION (only works for range analysis and not report generation)
# asumes all ranges are available as buttons -> so for end of line ranges you have to set it to the old system
# or add the missing CHECK FOLD CALL options to MISSING_BUTTONS (use right order)
NEW_RANGE_DETECTION=False
#MISSING_RANGES=[CHECK,FOLD,CALL] this way but only the ones that dont have buttons but are actual ranges
#MISSING_RANGES=[CALL]
MISSING_RANGES=[FOLD]
#MISSING_RANGES=[]

PREFLOP = False
#PREFLOP = True

# HAND QUIZZ0R
HAND_QUIZ = True #IMPORTANT set back to False if doing normal report generation because it enables save 0% hands and impacts speed alot
#HAND_QUIZ = False
MIN_QUIZ_WEIGHT = 0.5  #minimal combocount of hand in range...low weight combos often have weird/off strategy & dont effect ev much
MIN_ACTION_FREQ = 0.5 #minimal frequency with which "best" action is taken
MIN_EV_DIFF = 0 #minimal EV differnce between best and 2nd best desition (in monker chips) use 0 if no idea
MAX_EV_DIFF = 100 #maximal EV difference between best and 2nd best desition (in monker chips) use 100 if no idea
PRINT_EV_ERROR = 0.1 #prints summary of hands where error is bigger than this (in monker chips)
SHOW_SOLUTION=True # show / dont show solution
SHOW_STRATEGY=False #MAKES NO SENSE FOR NOW # show / dont show spot startegy when hitting summary

#Range Analysis
RANGE_ANALYSIS_VIEW_TYPES = ["MADE_HANDS", "DRAWS", "BLOCKERS", "DRAWS_BLOCKERS","FLUSH","STRAIGHT",
                             "BOARD_RANKS", "KEY_CARDS","POCKET_PAIRS","RANKS","SUITS",
                             "PREFLOP_PAIRS_HIGH_CARD","PREFLOP_SUITS","PREFLOP_HIGH_CARD",
                             "PREFLOP_CONNECTEDNESS"]
EXCLUDE_DEFAULT = True
PRINT_TOTAL_WEIGHTS = True
EV_FILTER_CONDITION=[10,50,100,300,600,1000,2000]