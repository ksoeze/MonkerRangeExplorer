#!/usr/bin/env python3
# board.py ---
#
# Filename: board.py
# Description:
# Author: Johann Ertl
# Maintainer:
# Created: Don Mar 17 10:47:22 2016 (+0100)
# Version:
# Last-Updated:
#           By:
#     Update #: 0
# URL:
# Keywords:
# Compatibility:
#
#

# Commentary:
#
# Ignores 2nd 2 pair on paired board: Q5 is not in list on AQ544 board
# HILO not working correctly [16-11-2017]
#

# Change Log:
#

# Code:

from monker_automation.utils import *
from itertools import combinations
from itertools import chain

def parse_board(board=''):
    current_board = []
    parsing_board = board
    parsing_board = parsing_board.replace(" ", "")

    # check if valid length and known chars
    if len(parsing_board) == 0 or len(parsing_board) > 10:
        return current_board
    for x in parsing_board:
        if x in RANKS or x in SUITS or x in RANDOM_RANKS or x in RANDOM_SUITS:
            continue
        else:
            return current_board
    # parse board
    for x in RANDOM_BOARD:
        if len(parsing_board) == 0:
            current_board.append(x)
            continue
        if parsing_board[0] in RANKS or parsing_board[0] in RANDOM_RANKS:
            x = x.replace(RANDOM_CARD[0], parsing_board[0])
            parsing_board = parsing_board[1:]
        if len(parsing_board) == 0:
            current_board.append(x)
            continue
        if parsing_board[0] in SUITS or parsing_board[0] in RANDOM_SUITS:
            x = x.replace(RANDOM_CARD[1], parsing_board[0])
            parsing_board = parsing_board[1:]
        current_board.append(x)
    return current_board


def return_string(board, street="river"):
    board_str = ''
    for i in range(0, 3):
        for j in range(0, 2):
            if board[i][j] in RANKS or board[i][j] in SUITS:
                board_str = board_str + board[i][j]
    if street == "turn" or street == "river":
        for j in range(0, 2):
            if board[3][j] in RANKS or board[3][j] in SUITS:
                board_str = board_str + board[3][j]
    if street == "river":
        for j in range(0, 2):
            if board[4][j] in RANKS or board[4][j] in SUITS:
                board_str = board_str + board[4][j]
    return board_str


def compact_range(hand_range):
    # delets useless hands from hand range list ( for example KK if K is also in the range)
    hand_range_compact = []
    for x in hand_range:
        if not any([r in x for r in hand_range if r != x]):
            hand_range_compact.append(x)
    return hand_range_compact


def return_ranks(board):
    ranks = [r for r, s in board if r in RANKS]
    return sorted(ranks, key=lambda x: RANK_ORDER[x], reverse=True)


def return_suits(board):
    suits = [s for r, s in board if s in SUITS]
    suits = [(suits.count(x), x) for x in SUITS if suits.count(x) != 0]
    return sorted(suits, key=lambda tup: tup[0], reverse=True)


def possible_flush_or_fd_ranks(board, suit):
    flush_ranks = [r for r, s in board if (s == suit and r in RANKS)]
    possible_flush_ranks = [r for r in RANKS if not r in flush_ranks]
    return possible_flush_ranks[0:-1]


def return_flushes(board):
    flush_suit = [s for c, s in return_suits(board) if c > 2]
    if not flush_suit:
        return []
    return [r + flush_suit[0] * 2 for r in possible_flush_or_fd_ranks(board, flush_suit[0])]


def return_flush_blockers(board):
    flushes = return_flushes(board)
    if not flushes:
        return []
    return [x[0:-1] for x in flushes]


def return_kickers(board):
    ranks = return_ranks(board)
    return [r for r in RANKS if r not in ranks]


def return_flushdraws(board):
    fd_suits = [s for c, s in return_suits(board) if c == 2]
    if not fd_suits:
        return ([], [])
    if len(fd_suits) == 2:
        return ([r + fd_suits[0] * 2 for r in possible_flush_or_fd_ranks(board, fd_suits[0])],
                [r + fd_suits[1] * 2 for r in possible_flush_or_fd_ranks(board, fd_suits[1])])
    else:
        return ([r + fd_suits[0] * 2 for r in possible_flush_or_fd_ranks(board, fd_suits[0])], [])


def return_rank_counts(board):
    ranks = return_ranks(board)
    rank_count = [[], [], [], []]
    for i in range(0, 4):
        rank_count[i] = list(set(r for r in ranks if ranks.count(r) == (i + 1)))
    for i in rank_count:
        i.sort(key=lambda x: RANK_ORDER[x], reverse=True)
    return rank_count


def hand_board_intersections(board):  # not including full +
    ranks = return_ranks(board)
    rank_count_list = return_rank_counts(board)
    if len(rank_count_list[0]) == len(ranks):
        sets = [str(r) * 2 for r in ranks]
        two_pair = [''.join(r) for r in combinations(ranks, 2)]
        return sets + two_pair + ranks
    if rank_count_list[2]:
        trips = []
        if rank_count_list[1]:
            if RANK_ORDER[rank_count_list[1][0]] > RANK_ORDER[rank_count_list[2][0]]:
                trips.append(rank_count_list[1][0])
        else:
            trips = [x * 2 for x in rank_count_list[0]
                     if RANK_ORDER[x] > RANK_ORDER[rank_count_list[2][0]]]
        return trips
    if rank_count_list[1]:
        trips = rank_count_list[1]
        two_pair = []
        possible_2_pair_ranks = [rank for rank in rank_count_list[0]
                                 if RANK_ORDER[rank] > RANK_ORDER[rank_count_list[1][0]]]
        if len(possible_2_pair_ranks) >= 2:
            two_pair = [''.join(possible_2_pair_ranks[0] + r)
                        for r in possible_2_pair_ranks[1:]]
        pairs = rank_count_list[0]
        return trips + two_pair + pairs  # quads+fulls+trips+two_pair+pairs
    return []


def return_fulls_or_better(board):
    ranks = return_ranks(board)
    rank_count_list = return_rank_counts(board)
    if rank_count_list[3]:
        return []
    if rank_count_list[2]:
        quads = [rank_count_list[2][0]]
        if rank_count_list[1]:
            quads.append(rank_count_list[1][0] * 2)
        return sorted(quads, key=lambda x: RANK_ORDER[x[0]], reverse=True)
    if rank_count_list[1]:
        quads = [r * 2 for r in rank_count_list[1]]
        fulls = [''.join(r + r) for r in rank_count_list[0]]
        fulls = fulls + [x + y for x in rank_count_list[0]
                         for y in rank_count_list[1]]
        if len(rank_count_list[1]) == 2:
            fulls = fulls + [''.join(rank_count_list[1][0]) +
                             ''.join(rank_count_list[1][1])]
        fulls = sort_fulls(ranks, fulls)
        return quads + fulls
    return []


def return_full_blockers(board):
    board_only_ranks = return_rank_counts(board)[0]
    board_only_ranks = parse_board(''.join(board_only_ranks))
    intersections = hand_board_intersections(board_only_ranks)
    blockers = []
    for hand in intersections:
        if len(hand) == 2:
            if hand[0] != hand[1]:
                blockers.append(hand)
        else:
            blockers.append(hand)
    return blockers


def return_str_flushes(board):
    straights = list(chain.from_iterable(return_straights(board)))
    flush_suit = [s for c, s in return_suits(board) if c > 2]
    str_flush = []

    if not (straights and flush_suit):
        return []

    for straight in STRAIGHTS:
        str_flush_cards = [c for c in straight if c + flush_suit[0] not in board]
        if len(str_flush_cards) == 2:
            str_flush.append(
                str_flush_cards[0] + flush_suit[0] + str_flush_cards[1] + flush_suit[0])
    return str_flush


def return_str_flush_blockers(board):
    str_flushes = return_str_flushes(board)
    if str_flushes:
        return [str_flushes[0][:2], str_flushes[0][2:4]]
    else:
        return []


def return_straights(board):
    ranks = return_ranks(board)
    straights = []
    straight_rank = {}

    for s in STRAIGHTS:
        straight_combo = []
        for r in combinations(ranks, 3):
            stra = ''.join([x for x in s if x not in r])
            if len(stra) == 2 and stra not in straights:
                straight_combo.append(
                    ''.join(sorted(stra, key=lambda x: RANK_ORDER[x], reverse=True)))
                straight_rank[''.join(
                    sorted(stra, key=lambda x: RANK_ORDER[x], reverse=True))] = STRAIGHTS.index(s)
        straight_combo.sort(key=lambda x: (
            RANK_ORDER[x[0]], RANK_ORDER[x[1]]), reverse=True)
        straights += straight_combo
    straights = list(dict.fromkeys(straights))
    straight_categories = [[], [], [], [], [], [], [], [], [], []]
    for item in straights:
        index = straight_rank[item] - straight_rank[straights[0]]
        straight_categories[index].append(item)
    return straight_categories


def return_straight_draws(board):
    ranks = return_ranks(board)
    if len(ranks) == 5:
        return {"wraps": [], "oesd": [], "gs": []}
    next_card_straight_hands = possible_straights_on_next_card(board)
    straight_hands = list(chain.from_iterable(return_straights(board)))
    gs_or_oesd = [hand for card in next_card_straight_hands for hand in next_card_straight_hands[card]
                  if hand not in straight_hands]
    any_4_card_straight_combo = [
        combo1 + combo2 for combo1 in gs_or_oesd for combo2 in gs_or_oesd]
    any_4_card_straight_combo = [''.join(sorted(set(
        hand), key=lambda x: RANK_ORDER[x], reverse=True)) for hand in any_4_card_straight_combo]
    any_4_card_straight_combo = list(set(any_4_card_straight_combo))

    def is_straight(hand, straight_hands):
        for straight in straight_hands:
            if (straight[0] in hand) and (straight[1] in hand):
                return True
        return False

    any_4_card_straight_combo = [
        draw for draw in any_4_card_straight_combo if not is_straight(draw, straight_hands)]

    hand_straight_outs = {}
    hand_straight_nuttynes = {}

    for hand in any_4_card_straight_combo:
        hand_straight_outs[hand] = []
        hand_straight_nuttynes[hand] = []
        for hand_combo in combinations(hand, 2):
            combo = ''.join(
                sorted(hand_combo, key=lambda x: RANK_ORDER[x], reverse=True))
            for r in RANKS:
                if combo in next_card_straight_hands[r]:
                    if r not in hand_straight_outs[hand]:
                        hand_straight_outs[hand].append(r)
                        hand_straight_nuttynes[hand].append(
                            next_card_straight_hands[r].index(combo))

    any_4_card_straight_combo = sorted(any_4_card_straight_combo, key=lambda x: (
        len(hand_straight_outs[x]), (100 - sum(hand_straight_nuttynes[x]), x)), reverse=True)

    for combo in combinations(any_4_card_straight_combo, 2):
        if hand_straight_outs[combo[0]] == hand_straight_outs[combo[1]]:
            if len(combo[0]) > len(combo[1]):
                if combo[1] in combo[0] and combo[0] in any_4_card_straight_combo:
                    any_4_card_straight_combo.remove(combo[0])
            else:
                if combo[0] in combo[1] and combo[1] in any_4_card_straight_combo:
                    any_4_card_straight_combo.remove(combo[1])

    draws = {"wraps": [], "oesd": [], "gs": []}
    for hand in any_4_card_straight_combo:
        outs = len(hand_straight_outs[hand])
        nuttynes = sum(hand_straight_nuttynes[hand])
        if outs >= 5 and nuttynes < 5 or outs == 4 and nuttynes < 4 or outs == 3 and nuttynes < 3:
            draws["wraps"].append(hand)
        elif outs >= 3 and nuttynes < 6 or outs == 2 and nuttynes < 2:
            draws["oesd"].append(hand)
        elif outs >= 2 and nuttynes < 6 or outs == 1 and nuttynes < 2:
            draws["gs"].append(hand)
    for item in draws:
        draws[item] = compact_range(draws[item])
    return draws


def return_straight_blocker_pairs(board):
    blockers = []
    straights = return_straights(board)
    if not straights:
        return blockers
    pairs = return_pairs(board)
    for p in pairs:
        for s in straights[0]:
            if p[0] in s:
                blockers.append(p)
    blockers = list(dict.fromkeys(blockers))
    return blockers


def possible_straights_on_next_card(board):
    next_card = {x: [] for x in RANKS}
    for card in next_card:
        next_card[card] = list(chain.from_iterable(
            return_straights(board + [card + "b"])))
    return next_card


def sort_fulls(ranks, fulls):
    sort_fulls = []
    for i in fulls:
        if ranks.count(i[0]) == 2 or i[0] == i[1]:
            sort_fulls.append(i)
        else:
            sort_fulls.append(i[1] + i[0])
    fulls = sorted(sort_fulls, key=lambda x: (
        RANK_ORDER[x[0]], RANK_ORDER[x[1]]), reverse=True)
    return [''.join(sorted(full, key=lambda x: RANK_ORDER[x], reverse=True)) for full in fulls]


def return_pairs(board):
    ranks = return_ranks(board)
    pairs = []
    for r in RANKS:
        if r not in ranks:
            pairs.append(''.join(r + r))
    return pairs


def return_over_pairs(board):
    ranks = return_ranks(board)
    op = []
    for r in RANKS:
        if RANK_ORDER[r] > RANK_ORDER[ranks[0]]:
            op.append(''.join(r + r))
    return op


def return_middle_pairs(board):
    ranks = return_ranks(board)
    ranks = list(dict.fromkeys(ranks))
    mp = []
    for r in RANKS:
        if RANK_ORDER[r] < RANK_ORDER[ranks[0]] and RANK_ORDER[r] > RANK_ORDER[ranks[1]]:
            mp.append(''.join(r + r))
    return mp


def best_low_board(hand, low_ranks):
    if len(
            low_ranks) == 2:  # low draw...just add random low card and proceed (trying 8 going down from there until card is not in ranks)
        for i in sorted(LOW_CARDS, key=lambda x: LOW_RANK_ORDER[x], reverse=True):
            if i not in low_ranks:
                low_ranks.append(i)
                break
    if len(low_ranks) >= 3:
        possible_low_hands = [sorted(list(hand + board), key=lambda x: LOW_RANK_ORDER[x]) for board in
                              combinations(low_ranks, 3)
                              if hand[0] not in board and hand[1] not in board]
        if possible_low_hands:
            return sorted(possible_low_hands, key=lambda x: (LOW_RANK_ORDER[x[4]], LOW_RANK_ORDER[x[3]],
                                                             LOW_RANK_ORDER[x[2]
                                                             ], LOW_RANK_ORDER[x[1]],
                                                             LOW_RANK_ORDER[x[0]]))[0]
        else:
            return []
    return []


def return_lows(board):
    ranks = return_ranks(board)
    ranks = set(ranks)
    low_board_ranks = [rank for rank in ranks if rank in LOW_CARDS]
    low_3_board_ranks = [board for board in combinations(low_board_ranks, 3)]
    low_hands = {}
    for hand in combinations(LOW_CARDS, 2):
        if best_low_board(hand, low_board_ranks):
            low_hands.update({hand: best_low_board(hand, low_board_ranks)})
    for hand in low_hands:
        low_hands[hand] = sorted(
            low_hands[hand], key=lambda x: LOW_RANK_ORDER[x])
        # print("Low Hand {} with the 2 Cards {}".format(low_hands[hand],hand))

    low_hands_sorted = list(sorted(low_hands.keys(), key=lambda x: (LOW_RANK_ORDER[low_hands[x][4]],
                                                                    LOW_RANK_ORDER[low_hands[x][3]],
                                                                    LOW_RANK_ORDER[low_hands[x][2]],
                                                                    LOW_RANK_ORDER[low_hands[x][1]],
                                                                    LOW_RANK_ORDER[low_hands[x][0]])))
    return [''.join(sorted(low, key=lambda x: LOW_RANK_ORDER[x])) for low in low_hands_sorted]

def test():
    board_string = "5s6d5c7dTc"
    sample_board = parse_board(board_string)
    # ranks = return_ranks(sample_board)

    # print(sample_board)
    # print(return_ranks(sample_board))
    # print(return_suits(sample_board))
    # print(return_fulls_or_better(board)
    # print(return_flushes(sample_board))
    # print(return_flushdraws(sample_board,'c'))
    # print(rank_count(return_ranks(sample_board)))
    print(return_full_blockers(sample_board))
    # print(return_string(sample_board,"river"))
    # print(return_straights(sample_board))

    # print(return_straight_draws(sample_board))
    # print(return_straight_blocker_pairs(sample_board))
    # print(return_straight_draws_categories(sample_board))
    # print(return_str_flushes(sample_board))
    # print(return_str_flush_blockers(sample_board))
    # print(return_next_cards("Ks4s3c",False))
    # print(return_lows(board))
    # print(pairs(ranks))
    # print(return_kicker(ranks))
    # print(return_rank_counts(ranks))


if __name__ == '__main__':
    import timeit
    test()
    # print((timeit.timeit("test()", setup="from __main__ import test",number=1000)))

#
# board.py ends here
