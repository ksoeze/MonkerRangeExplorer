#!/usr/bin/env python3

from monker_automation.utils import *
from monker_automation.views import get_view
from monker_automation.views import view_item_to_str
import os


def read_range_file(filename):
    range_list = []
    with open(filename, "r") as f:
        f.readline()  # skip first line
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
        if item[0] in RANKS and item[1] in SUITS:  # flushblocker
            if item in hand_list:
                return True
            else:
                return False
        elif item[0] in SUITS and item[1] in SUITS:  # random flush
            if item[0] in suits and suits.count(item[0]) >= 2:
                return True
            else:
                return False
        elif item[0] in RANKS and item[0] == item[1]:  # pocketpair
            if item[0] in ranks and ranks.count(item[0]) >= 2:
                return True
            else:
                return False
        elif item[0] in RANKS and item[1] in RANKS:  # 2 different ranks
            if item[0] in ranks and item[1] in ranks:
                return True
            else:
                return False
        return False
    elif len(item) == 3:
        if item[0] in RANKS and item[1] in SUITS and item[2] in SUITS:  # specific flush
            if item[:2] in hand_list and suits.count(item[2]) >= 2:
                return True
            else:
                return False
        elif item[0] in RANKS and item[1] in RANKS and item[2] in RANKS:  # oesd/wrap stuff
            if item[0] in ranks and item[1] in ranks and item[2] in ranks:
                return True
            else:
                return False
        return False
    elif len(item) == 4:  # wrap
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
    results = [[line, 0, 0] for line in view]
    results.insert(0, ["Total", 0, 0])
    results.append(["Other", 0, 0])
    for hand_line in range_list:
        match = False
        results[0][1] += hand_line[1]
        results[0][2] += hand_line[2]
        for i in range(len(view)):
            if hand_in_range(hand_line[0], view[i]):  # match hand
                results[i+1][1] += hand_line[1]  # weight count
                results[i+1][2] += hand_line[2]  # ev count total
                match = True
                if exclude:
                    break  # if exclude is enabled only count first match in view list
        if not match:  # no view match...add to "Other"
            results[-1][1] += hand_line[1]
            results[-1][2] += hand_line[2]
    return results


def total_counts(results):
    totals = [[line[0], 0, 0] for line in results[0][1]]
    for action, result in results:
        for i in range(len(totals)):
            totals[i][1] += result[i][1]
    return totals


def calc_percent(combo_list, reference):
    percent_list = []
    if type(reference) == list:
        for item, ref in zip(combo_list, reference):
            value = item/ref*100
            value = '{}'.format(round(value, 2))
            percent_list.append(value)
    elif type(reference) == float:
        for item in combo_list:
            value = item/reference*100
            value = '{}'.format(round(value, 2))
            percent_list.append(value)
    return percent_list


def org_print_result_matrix(matrix, filename):
    for line in matrix:
        print(line)
    with open(filename, 'w') as f:
        for line in matrix:
            output = "|" + '|'.join(line) + "|" + "\n"
            f.write(output)


def strategy_overview(actions, view):
    hand_lists = []
    results = []
    try:
        for action in actions:
            file_name = os.path.join(RANGE_FOLDER, action + ".csv")
            print(file_name)
            hand_lists.append((action, read_range_file(file_name)))
    except:
        print("Something went wrong reading range files...")
        exit()
    for action, hand_list in hand_lists:
        results.append((action, process_view(hand_list, view, True)))
    result_text_matrix = []
    column = [view_item_to_str(result_line[0])
              for result_line in results[0][1]]
    column = ["Description"]+column
    result_text_matrix.append(column)
    totals = total_counts(results)
    all_combos = [result_line[1] for result_line in totals]
    column = all_combos
    column = ["Total %"]+calc_percent(column, totals[0][1])
    result_text_matrix.append(column)

    for action, result in results:
        counts = [result_line[1] for result_line in result]
        column = [action]+calc_percent(counts, all_combos)
        result_text_matrix.append(column)
        column = ["relative %"]+calc_percent(counts, counts[0])
        result_text_matrix.append(column)
    result_text_matrix = [*zip(*result_text_matrix)]
    return result_text_matrix


def test():
    board = "KdJh5h"
    view = [["KK"]]
    view = get_view(board, VIEW_TYPES[0])
    range_list = read_range_file(CHECK_RANGE_FILE)
    print(range_list[0])
    # exclude means we exclude ranges like in monker view
    view_counts = process_view(range_list, view, exclude=True)
    view_counts.sort(key=lambda x: x[1])
    for item in view_counts:
        print(item)


if (__name__ == '__main__'):
    test()
