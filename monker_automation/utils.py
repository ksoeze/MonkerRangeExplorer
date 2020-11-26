#!/usr/bin/env python


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

VIEW_FOLDER = "/media/johann/MONKER/monker/Views/"
DEFAULT_VIEW_NAME = "OVERVIEW"
TOP_VIEW_LINE = "180\n"
MIN_WEIGHT = 0.001 #0.001

# custom views


# range constants

RANGE_FOLDER = "/media/johann/MONKER/monker/ranges/"

# gui reader constants

BACK_CO = (3885, 923)
CHECK_CO = (3955, 925)
BET_CO = (4039, 925)
# BUTTONS_CO = [(3955, 925), (4039, 925), (4123, 925), (4200, 925)]
BOARD_CLICK = (4000, 255)
LINE_CLICK = (4040, 1000)
# index 0 is for 1 range; index 2 for 2 ranges etc
RANGE_CO = [[(4400, 95)],
            [(4400, 95), (5400, 95)],
            [(4400, 95), (4900, 95), (5400, 95)],
            [(4400, 95), (4750, 95), (5050, 95), (5400, 95)],
            [(4400, 95), (4650, 95), (4920, 95), (5150, 95), (5400, 95)],
            [(4400, 95), (4600, 95), (4820, 95),
             (5000, 95), (5200, 95), (5400, 95)],
            ]

SAVE_OK = (4648, 637)
CSV_SELECT = (4577, 534)
FILE_TEXT = (4592, 602)
ZERO_HANDS_SELECT = (4664, 575)
FILTER_Y_OFFSET = 10

BOARD_SCREEN_REGION = (3842, 578, 450, 450)
RANGE_SCREEN_REGION = (4298, 2, 1185, 98)
FILTER_SCREEN_REGION = (4963,967,500,80)

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
                "35": "35.png", "40": "40.png", "50": "50.png", "60": "60.png",
                "66": "66.png", "70": "70.png", "75": "75.png", "80": "80.png",
                "90": "90.png", "100": "100.png", "AllIn": "allin.png"}
BUTTON_FILES_FOLDER = "/home/johann/code/monker_automation/monker_automation/buttons/"
BUTTON_REGION = (3940, 915, 4200, 931)
CHECK_CALL_REGION = (3940, 915, 4000, 931)  # restrict for performance reasons

# info tree creation
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
DEFAULT_REPORT_DIRECTORY = "/home/johann/Documents/poker/monker-documentation/MonkerReports/"
DEFAULT_REPORT_VIEW_DIR = "/home/johann/Documents/poker/monker-documentation/MonkerReports/views/"
DEFAULT_REPORT_MATCHER_DIRECTORY = "/home/johann/Documents/poker/monker-documentation/MonkerReports/matcher/"
STRATEGY_PNG_NAME = "strat.png"
RANGE_PNG_NAME = "range.png"
VIEW_PDF_NAME = "view.pdf"
FILTER_PNG_NAME="filter.png"
# STRATEGY_PDF_NAME = "strategy.pdf"
REPORT_PDF_NAME = "report.pdf"
TABLE_PNG_NAME = "table.png"
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

# ZEILEN mit # sind nur Kommentare
# View AUSWAHL = ["DEFAULT", "MADE_HANDS", "DRAWS", "BLOCKERS", "DRAWS_BLOCKERS", "CUSTOM"]
SCRIPT_VIEW_TYPE = ["DEFAULT", "MADE_HANDS"]
# SCRIPT_VIEW_TYPE = ["DEFAULT","MADE_HANDS", "DRAWS", "BLOCKERS", "DRAWS_BLOCKERS"]
# SCRIPT_VIEW_TYPE = ["DEFAULT","MADE_HANDS","BLOCKERS"]

# low blank, medium to high 2 fd card, A (or next non pairing card) "blank",
# top card pairing, bottom card paring, main oesd low card, gs card high card,
# flush blank, flush pairing (top or 2nd card paring), A (nf card) flush

# TURN_CARDS = ["2h","Ks","Ah","Qh","7h","9h","Jh","5d","Qd","Ad"]
# TURN_CARDS = ["8h","Kd","Kh","7h","2h","Ah","5h","Ts","3s","As"]
# TURN_CARDS = ["5s","5d","5c", "Ac", "Jh", "7s", "9h", "9c", "Ts", "Th", "Qh", "Ks"]
# TURN_CARDS = ["5h","5c", "Qc", "Th", "7s", "9h", "As", "Kh", "Jc","6d"]
# TURN_CARDS = ["8h","8c", "6c", "Ah", "7s", "3h", "2h", "Kh", "Jc","6d","Qs"]
# ["As","Ks","5s","Ts","9c","9s"]
TURN_CARDS = ["Ah","Kc","Jh","Tc","7c","6d","4d","2c"]
TURN_CARDS = ["Ac","Ks","Kc","Qh","Qd","Jc","Js","Tc","9d","7h","6c","4d","2c"]
# TURN_CARDS = ["Ac","Kc","Qc","Jc","Tc","9c","8c","7c","6c","5c","4c","3c","2c"]
# TURN_CARDS = []
# RIVER_CARDS = ["2h","Kd","Ah","7h", "Qd", "Kc"]
# RIVER_CARDS = ["4h","Ah","Kh","Qh","Jd","3d","Ad","Qd","7h","6h"]
# RIVER_CARDS = ["4h","Ah","Qh","Th","3d","Ad","Qd","3s","As","Ts"]
# RIVER_CARDS = ["4h","Ad","Ac","Th","Jh","4d","9c","6c"]
# RIVER_CARDS = ["4h","Ah","3h","6h","8s","As","3s","7c","Kc","Qc"]
# RIVER_CARDS = ["8h","As","Ac","7h","8s","3s","5d","4c","3c","2c","Kc","Jh"]
# RIVER_CARDS = ["4h","6h","Ah","Kh","4d","Ad","7c","Qd"]
# RIVER_CARDS = ["4h","Ah","Th","9h","3d","Ad","Qd"]
# RIVER_CARDS = ["8h","6h","4h","Ah","As","7d","2d","3h","Kh","Qh"]
# RIVER_CARDS = ["8h","Ah","7c","Kh","8s","As","8d","Ad","7d"]
# RIVER_CARDS = ["8h","As","Ac","7h","8s","3s","5d","4c","3c","2c","Kc"]
# RIVER_CARDS = ["Qh","Ah","Jh","6h","8s","Ks","As","Td","3c","4c","7d"]
# RIVER_CARDS=["Th","Ah","7h","8h","Ts","As","5s","Kd","Qd"]
# RIVER_CARDS=["6h","Ah","Tc","Kh","3s","Ks","Js"]
# RIVER_CARDS=["2h","Ah","9h","Kd","Ad","Qh","7h"]
# RIVER_CARDS=["4h","Ah","Qh","Th","Jh","3d","Kd","9d"]
# RIVER_CARDS=["2h","Kh","9h","Ah","Ad","Qh","Th","7h","6h"]
# RIVER_CARDS=["2h","Ah","Qh","Ks","Qs","Jh","5h","8h","Th"]
# RIVER_CARDS=["4h","Ah","Qh","3s","Js","Ks","8h"]
# RIVER_CARDS=["4h","Kh","Ah","Qh","7d","3s","Js","Ks","8h"]
# RIVER_CARDS=["4h","Ah","Qh","3s","Js","Ks","8h"]
# RIVER_CARDS=["4h","Kh","Ah","Jh","7h","3s","Js","Ks","8h","9h"]
# RIVER_CARDS=["3d","Ad","Ah","4h","8s","As","2c","3h","Kh","Qh"]
# RIVER_CARDS = ["Ac","Kc","Qc","Jc","Tc","9c","8c","7c","6c","5s","4c","3c","2c"]
# RIVER_CARDS = ["2c","Ac","Ts","Ks","7s","Jc","Qh","2h","Ah","Jh","Kh"]
# RIVER_CARDS = ["3c", "Ac", "Kc", "Jc", "9d", "8c", "6c", "Qc", "Tc", "7d", "5d", "Ad", "Td"]
# RIVER_CARDS = ["Ah", "Kh", "Qh", "Jh", "Th", "8h", "7d", "4h", "Ad", "7d", "4d"]
# RIVER_CARDS = ["2c", "Ad", "Th","Kd","Jh"]
RIVER_CARDS = ["Ac","Ks","Kc","Qh","Qd","Jc","Tc","9d","7c","6c","6d"]
RIVER_CARDS = []
#RIVER_CARDS = ["9h", "9d", "Qc", "Tc", "Ac", "Ad"]
# z.b. [[RAISE,RAISE]] für bet, vs bet und vs raise lines only
INVALID_SEQUENCES = [[BET, RAISE]]
INVALID_SEQUENCES = [[RAISE, RAISE]]
#INVALID_SEQUENCES = []

# siehe lines.txt
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
POSSIBLE_BET_RAISE = ["25", "33", "50", "66", "100", "AllIn"]
#POSSIBLE_BET_RAISE = ["50","100","AllIn"]
POSSIBLE_BET_RAISE = ["MIN","33","40","66","100", "AllIn"]
#POSSIBLE_BET_RAISE = ["30","50","70","100", "AllIn"]
#POSSIBLE_BET_RAISE = ["33","50","100","AllIn"]
#POSSIBLE_BET_RAISE = ["50","100", "AllIn"]
POSSIBLE_BET_RAISE = ["MIN","10","25","30","33","40","50","66","70","75","100","AllIn"]

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
NEW_RANGE_DETECTION=True
NEW_RANGE_DETECTION=False
#MISSING_RANGES=[CHECK,FOLD,CALL] this way but only the ones that dont have buttons but are actual ranges
#MISSING_RANGES=[CALL]
#MISSING_RANGES=[FOLD]
MISSING_RANGES=[]

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
                             "PREFLOP_PAIRS_HIGH_CARD","PREFLOP_SUITS","PREFLOP_HIGH_CARD"]
EXCLUDE_DEFAULT = True
PRINT_TOTAL_WEIGHTS = True
EV_FILTER_CONDITION=[10,50,100,300,600,1000,2000]
