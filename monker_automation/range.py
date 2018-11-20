#!/usr/bin/env python3

from monker_automation.utils import *
from monker_automation.views import get_view


def read_range_file(filename):
    range_list = []
    with open(filename, "r") as f:
        f.readline() # skip first line
        for line in f:
            result_list = line.split(",")
            result_list[1] = float(result_list[1])
            result_list[2] = float(result_list[2])
            range_list.append(result_list)
    return range_list


def hand_in_item(hand, item):
    hand_list = [hand[:2], hand[2:4], hand[4:6], hand[6:8]]
    ranks = [card[0] for card in hand_list]
    suits = [card[1] for card in hand_list]

    if len(item) == 1:
        if item in RANKS:
            if item in ranks:
                return True
            else:
                return False
        elif item in SUITS:
            if item in suits:
                return True
            else:
                return False
        return False
    elif len(item) == 2:
        if item[0] in RANKS and item[1] in SUITS: #flushblocker
            if item in hand_list:
                return True
            else:
                return False
        elif item[0] in SUITS and item[1] in SUITS: #random flush
            if item[0] in suits and suits.count(item[0]) >= 2:
                return True
            else:
                return False
        elif item[0] in RANKS and item[0] == item[1]: #pocketpair
            if item[0] in ranks and ranks.count(item[0]) >=2:
                return True
            else:
                return False
        elif item[0] in RANKS and item[1] in RANKS: #2 different ranks
            if item[0] in ranks and item[1] in ranks:
                return True
            else:
                return False
        return False
    elif len(item) == 3:
        if item[0] in RANKS and item[1] in SUITS and item[2] in SUITS: #specific flush
            if item[:2] in hand_list and suits.count(item[2]) >=2:
                return True
            else:
                return False
        elif item[0] in RANKS and item[1] in RANKS and item[2] in RANKS: #oesd/wrap stuff
            if item[0] in ranks and item[1] in ranks and item[2] in ranks:
                return True
            else:
                return False
        return False
    elif len(item) == 4: #wrap
        for r in item:
            if r not in RANKS or r not in ranks:
                return False
        return True
    return False

def hand_in_range(hand, range_list, exclude_list=[]):
    if type(range_list[0]) == str:
        matches_hand = True
        for i in exclude_list:
            if hand_in_item(hand, i):
                matches_hand = False
        if matches_hand == False:
            return False  
        for i in range_list:
            if hand_in_item(hand, i):
                return True
        return False
    elif type(range_list[0]) == list and len(range_list) == 2:
        matches_hand = True
        for i in exclude_list:
            if hand_in_item(hand, i):
                matches_hand = False
        if matches_hand == False:
            return False
        matches_hand = False
        for i in range_list[0]:
            if hand_in_item(hand, i):
                matches_hand = True
        if matches_hand == False:
            return False
        for i in range_list[1]:
            if hand_in_item(hand, i):
                return True
        return False
    return False


def process_view(range_list, view, exclude):
    processed_hands=[]
    results = []
    for item in view:
        cummulative_count = 0
        cummulative_ev = 0
        for hand_line in range_list:
            if exclude and hand_line[0] in processed_hands: # already matched before
                continue
            if hand_in_range(hand_line[0],item): # match hand
                cummulative_count += hand_line[1]
                cummulative_ev += hand_line[2]
                processed_hands.append(hand_line[0])
        print("{}: count:{} ev:{}".format(item, cummulative_count, cummulative_ev))
        ev = 0 if cummulative_count == 0 else cummulative_ev/cummulative_count
        results.append([item, cummulative_count, ev])
    return results

def test():
    board="KdJh5h"
    view = [["KK"]]
    view = get_view(board, VIEW_TYPES[0])
    range_list = read_range_file(CHECK_RANGE_FILE)
    print(range_list[0])
    view_counts = process_view(range_list, view, exclude=True) #exclude means we exclude ranges like in monker view
    view_counts.sort(key=lambda x:x[1])
    for item in view_counts:
        print(item)    

    
if (__name__ == '__main__'):
    test()
