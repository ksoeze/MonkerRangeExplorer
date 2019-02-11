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
RANDOM_BOARD = [RANDOM_CARD]*5
RANK_ORDER = {'A': 12, 'K': 11, 'Q': 10, 'J': 9, 'T': 8, '9': 7,
              '8': 6, '7': 5, '6': 4, '5': 3, '4': 2, '3': 1, '2': 0}
LOW_RANK_ORDER = {'K': 12, 'Q': 11, 'J': 10, 'T': 9, '9': 8,
                  '8': 7, '7': 6, '6': 5, '5': 4, '4': 3, '3': 2, '2': 1, 'A': 0}
LOW_CARDS = list("A2345678")
STRAIGHTS = [list("AKQJT"), list("KQJT9"), list("QJT98"), list("JT987"), list(
    "T9876"), list("98765"), list("87654"), list("76543"), list("65432"), list("5432A")]
INVALID_CHAR = '#'

# view constants
QUAD_BOARD_PAIR_GROUPING = [1, 1, 2, 2,3]
PAIRED_BOARD_FULL_OR_BETTER_GROUPING = [2, 2]
FLUSH_GROUPING = [1, 1, 2]
OVERPAIR_GROUPING = [1, 2]
FLUSH_GROUPING = [1, 1, 2]
SET_GROUPING = [1, 1]
PAIR_GROUPING = [1, 1]
MIDDLE_PAIR_GROUPING = [2]
VIEW_TYPES = ["DEFAULT", "MADE_HANDS", "DRAWS", "BLOCKERS", "CUSTOM", "DRAWS_BLOCKERS"]

VIEW_FOLDER = "/home/johann/monker/Views/"
DEFAULT_VIEW_NAME = "OVERVIEW"
TOP_VIEW_LINE = "180\n"

# custom views


# range constants

RANGE_FOLDER = "/home/johann/monker/ranges/"

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

SAVE_OK = (4648, 601)
CSV_SELECT = (4577, 534)
FILE_TEXT = (4592, 569)

BOARD_SCREEN_REGION = (3842, 578, 450, 450)
RANGE_SCREEN_REGION = (4298, 2, 1185, 98)

NUM_BACK = 10
DELETE_BOARD = 7
MOUSE_MOVEMENT_DEL = 0.1
CLICK_DELAY = 0.01
TYPE_DELAY = 0.01
SLEEP_AFTER_SAVE = 0.5
SLEEP_AFTER_FINISH = 1

FOLD = "FOLD"
BACK = "BACK"
CHECK = "CHECK"
CALL = "CALL"
BET = "BET"
RAISE = "RAISE"
POSSIBLE_BET_RAISE = ["40", "60", "80", "100", "AllIn"]
POSSIBLE_BET_RAISE = ["50", "100", "AllIn"]
POSSIBLE_BET_RAISE = ["20","30", "40", "50", "100", "AllIn"]
POSSIBLE_BET_RAISE = ["MIN","10","25","50","75","100","AllIn"]
#POSSIBLE_BET_RAISE = ["30","50", "70","100", "AllIn"]
POSSIBLE_BET_RAISE = ["50","100","AllIn"]
# POSSIBLE_BET_RAISE = ["30", "40","50", "70", "80","100", "AllIn"]
BUTTON_FILES = {"CHECK": "check.png", "CALL": "call.png", "MIN": "min.png", "10":"10.png","20": "20.png",
                "25":"25.png","30": "30.png",
                "35": "35.png", "40": "40.png", "50": "50.png", "60": "60.png", "66":"66.png","70": "70.png",
                "75":"75.png","80": "80.png", "100": "100.png", "AllIn": "allin.png"}
BUTTON_FILES_FOLDER = "/home/johann/code/monker_automation/monker_automation/buttons/"
BUTTON_REGION = (3930, 911, 4200, 935)
CHECK_CALL_REGION = (3930, 911, 4000, 936)  # restrict for performance reasons
MAX_BETS_RAISES = 2
QUIZ = False
PRINT_VIEWS = True

# info tree creation
LINE_START = "|"
MIN_FREQ = 10
MIN_RAISE_FREQ = 5

# standard lines

# 1 bet lines
CARD_DUMMY = ["Ah"]
OOP_BET = [LINE_START, ]
IP_BET = [LINE_START, CHECK]
OOP_X_BET = IP_BET+[CHECK]+CARD_DUMMY
IP_X_BET = OOP_X_BET+[CHECK]
OOP_X_X_BET = IP_X_BET+[CHECK]+CARD_DUMMY
IP_X_X_BET = OOP_X_X_BET+[CHECK]

# 2nd and 3rd barrel of IP and action vs bet
OOP_vsBET = [LINE_START, CHECK, BET]
IP_BET_BET = OOP_vsBET + [CALL] + CARD_DUMMY+[CHECK]
OOP_CALL_vsBET = IP_BET_BET + [BET]
IP_BET_BET_BET = OOP_CALL_vsBET + [CALL] + CARD_DUMMY+[CHECK]
OOP_CALL_CALL_vsBET = IP_BET_BET_BET + [BET]

# 2nd and 3rd barrel of OOP and action vs bet
IP_vsBET = [LINE_START, BET]
OOP_BET_BET = IP_vsBET+[CALL] + CARD_DUMMY
IP_CALL_vsBET = OOP_BET_BET + [BET]
OOP_BET_BET_BET = IP_CALL_vsBET + [CALL] + CARD_DUMMY
IP_CALL_CALL_vsBET = OOP_BET_BET_BET + [BET]

# one bet and face raise
IP_BET_vsRAISE = IP_BET+[RAISE]
OOP_BET_vsRAISE = OOP_BET+[RAISE]
IP_X_BET_vsRAISE = IP_X_BET + [RAISE]
OOP_X_BET_vsRAISE = OOP_X_BET + [RAISE]
IP_X_X_BET_vsRAISE = IP_X_X_BET + [RAISE]
OOP_X_X_BET_vsRAISE = OOP_X_X_BET + [RAISE]

# vs delay bet
IP_X_vsBET = OOP_X_BET+[BET]
OOP_X_vsBET = IP_X_BET+[BET]
IP_X_X_vsBET = OOP_X_X_BET+[BET]
OOP_X_X_vsBET = IP_X_X_BET+[BET]

# call once and then bet / donk
IP_CALL_BET=OOP_BET_BET+[CHECK]
OOP_BET_vsBET=IP_CALL_BET + [BET]
OOP_CALL_BET=OOP_vsBET+[CALL]
IP_BET_vsBET=OOP_CALL_BET+[BET]

# analysis

DEFAULT_VIEW_RESULT_FILENAME = "/home/johann/code/monker_automation/RESULTS.org"
DEFAULT_REPORT_DIRECTORY = "/home/johann/Documents/poker/monker-documentation/MonkerReports/"
DEFAULT_REPORT_VIEW_DIR = "/home/johann/Documents/poker/monker-documentation/MonkerReports/views/"
DEFAULT_REPORT_MATCHER_DIRECTORY ="/home/johann/Documents/poker/monker-documentation/MonkerReports/matcher/"
STRATEGY_PNG_NAME = "strat.png"
RANGE_PNG_NAME = "range.png"
VIEW_PDF_NAME = "view.pdf"
#STRATEGY_PDF_NAME = "strategy.pdf"
REPORT_PDF_NAME = "report.pdf"
TABLE_PNG_NAME = "table.png"
RANGE_HEADER_PNG_NAME = "range_header.png"

# # developement constants

# DEBUG = True
# MACRO_FILE_LOCATION = "/home/johann/Documents/poker/oddsOracleMacros.csv"

# PPT_SERVER_PORT = "http://localhost:37890"
# TEST_QUERY = ("select avg(equity(hero, turn)) as EQUITY \n"
#               "from game='omahahi', \n"
#               "syntax='Generic', \n"
#               "hero='AA', \n"
#               "villain='KdQsTcJd', \n"
#               "board='Kc8s5s' \n")

# PPT_TRIAL = 100000  # omaha ranger: 300000 and 50000 for evaluation
# PPT_RANK_QUERY_TRIAL = 10000
# PPT_IN_RANGE_TRIAL = 50000
# PPT_NEXT_CARD_EQ_TRIAL = 100000
# PPT_MAX_SEC = 10
# PPT_THREAD_CNT = 8
# PPT_LOCATION = "/home/johann/usr/PPTOddsOracle/ui_jar/"
# # whole length including decimal point (minimal length = 0.0)
# PPT_NUM_DIGETS = 3
# PPT_GAME = "omahahi"  # std game
# PPT_SYNTAX = 'Generic'

# # ev calcs defaults

# STACKSIZE = 97.0
# POTSIZE = 6.5
# BETSIZE = 4
# RAISESIZE = 14
# RERAISESIZE = 35
# STREET = "flop"

# BET4_STACK = 100
# BET4_OPEN = 3
# BET4_3BET = 10
# BET4_POT = 14

# # gui constants

# INPUT_LENGTH = 50  # number of chars for standard range input line
# PRE_INPUT_LENTH = 40
# # number of chars reserved for start range...adjust if Freq and Equity Description arent alligned
# START_RANGE_WIDTH = 47
# SPACES_BEFORE_SUMMARY_LINE = 42
# PADX = 5  # std padding x
# PADY = 5  # std padding y
# BUTTON_PADX = 5
# FRAME_PADDING = "3 3 3 3"  # std padding for small frames
# RANGE_FRAME_PADDING = "3 50 3 3"
# PLAYER_FRAME_PADDING = "3 3 180 3"
# EV_PLAYER_FRAME_PADDING = "10 10 3 3"
# GENERAL_SETTING_PADDING = "10 10 10 10"
# FONT_SIZE = 9  # std font size
# FONT_FAM = 'Helvetica'
# FONT_FAM_MONO = 'monospace'
# TITLE = "OMAHA RANGE CRUSHER"
# MAIN_GEOMETRY = "2200x2000"
# TEXT_OUTPUT_HEIGHT = 60
# TEXT_OUTPUT_WIDTH = 140
# DOTS = "-----------------------------------------------------------"

# BET_VS_1_INFO = ("Hero subranges are ignored for EV calcs...only Hero Prerange + Hand and Villain Ranges\n"
#                  "Enter at least valid ranges for:\n"
#                  "Hero Pre, Villain Pre, Villain Subrange 1,2,4, Hero Hand\n"
#                  "Villain Range 1 is his value raise range; Range 2: call; Range 3: bluffraise; Range 4: fold (enter *)\n"
#                  "Selections are ignored for EV calcs...but freq and eq results next to ranges works as in range builder\n"
#                  "Betsizes are not checked for validity...\n"
#                  "For AI spots just enter bet or raise or reraisesize == stacksize")

# BET_VS_1_RESULT_STR = ("Some guidelines:\n"
#                        "Perfect polarised range when betting pot:\n"
#                        "Value:Bluff flop ~ 1:2.37 \n"
#                        "Value:Bluff turn ~ 1:1.25\n"
#                        "Value:Bluff river ~ 2:1 \n"
#                        "Alpha is % a bluff has to work for EV = 0 with 0% equity\n"
#                        "1-Alpha is % a player should defend vs perfectly polarised range\n"
#                        "Realisation factors are hard to estimate...\n"
#                        "Would guess R_vs_raise < R_vs_range < R_vs_call against most players in many situations\n"
#                        "Nutty draws...fd/gs etc can often realise more than their equity\n"
#                        "Weak made hands often realise a lot less than their equity\n"
#                        "Arguments for bet: \n"
#                        "- dont get raised off equity often (low raise feq + low equity vs raise range)\n"
#                        "- equity vs call is not much lower than equity vs range\n"
#                        "- equity vs folding range is low\n"
#                        "Defend vs Raise asumes villain plays on range 1 and folds range 3"
#                        "...")

# BET_VS_2_INFO = ("Hero subranges are ignored for EV calcs...only Hero Prerange + Hand and Villain Ranges\n"
#                  "Enter at least valid ranges for:\n"
#                  "Hero Pre, Villain1/2 Pre, Villain1 Subrange 1,2,4, Villain2 Subrange 1,2,4,  Hero Hand\n"
#                  "Villain Range 1 is the value raise range; Range 2: call; Range 3: bluffraise; Range 4: fold (enter *)\n"
#                  "Villain 2 acts after villain 1...Villain 2 ships range 1 4 value also when villain 1 calls/raises (unrealistic but 3 way ai are rare)\n"
#                  "Selections are ignored for EV calcs...but freq and eq results next to ranges works as in range builder\n"
#                  "(eq and freq are calculated vs selection of both other players)\n"
#                  "Betsizes are not checked for validity...\n")

# BET_VS_2_RESULT_STR = ("Some guidelines:\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "\n"
#                        "...")
# BET4_INFO = ("Enter Hand in question\n\n"
#              "If thinking about 4bet:\n"
#              "Enter your starting stack with V1; your open/dead amount; V1 3bet size; total potsize after 3bet\n"
#              "Takes V1 pre range as start (=3bet range); 5bet subrange 1; call rest and stacks off if equity > pot odds vs your hand\n"
#              "(not accurate in real game but vs AA is very slow calc)\n\n"
#              "If thinking about call 4bet:\n"
#              "Enter your starting stack with V1; your 3bet size; total potsize after 3bet\n"
#              "Takes V1 pre range as start (=4bet range); asumes perfect play from us vs V1 on the flop\n\n"
#              "Betsizes are not checked for validity...\n")

# BET4_RESULT = ("\n"
#                "...see logging output\n")
