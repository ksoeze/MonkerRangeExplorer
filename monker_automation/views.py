#!/usr/bin/env python3
import random
import re

from monker_automation.utils import *
import monker_automation.board as board_util
import os
import logging
import pprint
import itertools

def regroup_list(hand_list, pattern):
    return_hand_list = []
    for i in pattern:
        if hand_list == []:
            return return_hand_list
        if len(hand_list) < i:
            return_hand_list.append(hand_list)
            return return_hand_list
        return_hand_list.append(hand_list[:i])
        hand_list = hand_list[i:]
    if hand_list != []:
        return_hand_list.append(hand_list)
    if return_hand_list: # when last item contains RANK+SUIT or RANK SUIT SUIT add SUIT bzw SUIT SUIT to last item # fd "hack"
        if return_hand_list[-1][-1]:
            if len(return_hand_list[-1][-1]) == 2 and return_hand_list[-1][-1][0] in RANKS and return_hand_list[-1][-1][1] in SUITS:
                return_hand_list[-1].append(return_hand_list[-1][-1][1])
            elif (len(return_hand_list[-1][-1]) == 3
                  and return_hand_list[-1][-1][0] in RANKS
                  and return_hand_list[-1][-1][1] in SUITS
                  and return_hand_list[-1][-1][2] in SUITS) :
                return_hand_list[-1].append(return_hand_list[-1][-1][1:3])
    return return_hand_list

def regroup_board_intersections(board):
    ranks = board_util.return_ranks(board)
    intersections = board_util.hand_board_intersections(board)

    sets = []
    top2 = []
    topbottom = []
    random2 = []
    pair = []

    for item in intersections:
        if len(item) == 2:
            if item[0] == item[1]:
                sets.append(item)
            elif item[0] == ranks[0] and item[1] == ranks[1]:
                top2.append(item)
            elif item[0] == ranks[0]:
                topbottom.append(item)
            else:
                random2.append(item)
        else:
            pair.append(item)

    return {"sets": sets, "top2": top2,
            "topbottom": topbottom,
            "random2": random2,
            "pair": pair}


def quad_board(board):
    view = []
    rank_count_list = board_util.return_rank_counts(board)
    pairs = [r * 2 for r in RANKS if r not in rank_count_list[3]]
    view += regroup_list(pairs,
                         QUAD_BOARD_PAIR_GROUPING)
    kicker_board = board_util.parse_board(''.join(rank_count_list[3]))
    kickers = board_util.return_kickers(kicker_board)
    view.append([kickers[0] + kickers[1], kickers[0] +
                 kickers[2], kickers[0] + kickers[3]])
    view.append([kickers[0]])
    return view


def trips_board(board):
    view = []
    rank_count_list = board_util.return_rank_counts(board)
    # str flushes
    view.append(board_util.return_str_flushes(board))
    # fulls or better
    view.append(board_util.return_fulls_or_better(board))
    overfulls = []
    for card in rank_count_list[0]:
        if RANK_ORDER[card] > RANK_ORDER[rank_count_list[2][0]]:
            overfulls.append(card * 2)
    # overfulls
    view.append(overfulls)
    # fulls
    pairs = [r * 2 for r in RANKS if r not in rank_count_list[2]]
    pairs = [pair for pair in pairs if pair not in overfulls]
    view += regroup_list(pairs,
                         QUAD_BOARD_PAIR_GROUPING)
    flushes = board_util.return_flushes(board)
    if flushes:
        flushes = [flushes[0][1:]]
        view.append(flushes)
        return view
    straights = board_util.return_straights(board)
    if straights[0]:
        view.append(straights[0] + straights[1])
    if not flushes or not straights:
        kicker_board = board_util.parse_board(''.join(rank_count_list[2]))
        kickers = board_util.return_kickers(kicker_board)
        view.append([kickers[0] + kickers[1], kickers[0] +
                     kickers[2], kickers[0] + kickers[3]])
    return view


def trips_board_blocker(board):
    view = []
    rank_count_list = board_util.return_rank_counts(board)
    str_flush_blocker = board_util.return_str_flush_blockers(board)

    view.append(str_flush_blocker)
    overfull_blocker = []

    for card in rank_count_list[0]:
        if RANK_ORDER[card] > RANK_ORDER[rank_count_list[2][0]]:
            overfull_blocker.append(card)

    view.append(overfull_blocker)
    pair_blockers = [p[0] for p in board_util.return_pairs(board)]
    pair_blockers = pair_blockers[:int(len(pair_blockers) // 1.5)]
    view += regroup_list(pair_blockers, QUAD_BOARD_PAIR_GROUPING)
    return view


def paired_board(board):
    view = []
    rank_count_list = board_util.return_rank_counts(board)

    intersections = board_util.hand_board_intersections(board)
    kickers = board_util.return_kickers(board)

    fd = board_util.return_flushdraws(board)

    # str flushes
    view.append(board_util.return_str_flushes(board))

    # fulls or better
    view += regroup_list(board_util.return_fulls_or_better(board),
                         PAIRED_BOARD_FULL_OR_BETTER_GROUPING)

    flushes = board_util.return_flushes(board)
    straights = board_util.return_straights(board)

    if flushes:
        # nf + trips
        view.append([[flushes[0]], rank_count_list[1]])
        # nf + overfull blocker
        view.append([[flushes[0]], [rank for rank in rank_count_list[0]
                                    if RANK_ORDER[rank] > RANK_ORDER[rank_count_list[1][0]]]])
        # fd + trips
        view.append([[flushes[0][1:]], rank_count_list[1]])
        # flushes
        view += (regroup_list(flushes, FLUSH_GROUPING))
        if straights[0]:
            # straights
            view.append(straights[0] + straights[1])
        # nf and 2nd nf blocker
        view.append([flushes[0][:2], flushes[1][:2]])
    elif straights[0]:
        # nutstraight + trips
        view.append([straights[0], rank_count_list[1]])
        # nutstraight + overfull blockers
        view.append([straights[0], [rank for rank in rank_count_list[0]
                                    if RANK_ORDER[rank] > RANK_ORDER[rank_count_list[1][0]]]])
        # nutstraight
        view.append(straights[0])
        # 2nd nutstraight
        if straights[1]:
            view.append([straights[1], rank_count_list[1]])
            view.append(straights[1])
        # 3rd nutstraight
        if straights[2]:
            view.append(straights[2])

    if not flushes and not straights[0]:
        # trips + kickers
        view.append([kickers[0] + intersections[0]])
        view.append([kickers[1] + intersections[0],
                     kickers[2] + intersections[0]])

    # trips
    view.append([intersections[0]])

    # add undertrips if possible
    if len(rank_count_list[1]) >= 2:
        view.append(rank_count_list[1][1])

    fd_1, fd_2 = board_util.return_flushdraws(board)
    straight_draws = board_util.return_straight_draws(board)
    overpairs = board_util.return_over_pairs(board)
    middlepairs = board_util.return_middle_pairs(board)
    if len(rank_count_list[0]) != 0:
        top_pair = rank_count_list[0][0]
    else: # turn double paired board
        top_pair = board_util.return_pairs(board)[0][0] # just use highcard...might give bad results

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd = [fd_1[0]]
        fd = [fd_1[0][1:]]
        if fd_2:
            nfd.append(fd_2[0])
            fd.append(fd_2[0][1:])
        # nfd + best 2 overpairs and best pair intersection on board
        view.append([nfd, overpairs[:2] + [top_pair]])
        # any fd with sd value
        view.append([fd, overpairs[:2] + [top_pair]])
        # any fd with any oesd or better
        if straight_draws["oesd"]:
            view.append([fd, straight_draws["wraps"] + straight_draws["oesd"]])
        # nfd no decent sd value
        view.append(nfd)
        # bare fd
        view.append(fd)

        # nfd blocker?
        view.append([a[:2] for a in nfd])
    if straight_draws["gs"] and not flushes:
        if straight_draws["oesd"]:
            # oesd straight draws + op or tp
            view.append([overpairs[:2] + [top_pair],
                         straight_draws["wraps"] + straight_draws["oesd"]])
            # better straight draws
            view.append(straight_draws["wraps"] + straight_draws["oesd"])

        # gs straight draws + sd value
        view.append([overpairs[:2] + [top_pair],
                     straight_draws["gs"]])

        # gs draws
        view.append(straight_draws["gs"])

    if overpairs:
        view += regroup_list(overpairs, OVERPAIR_GROUPING)

    # top pair
    # middle pairs
    if RANK_ORDER[top_pair] > RANK_ORDER[rank_count_list[1][0]]:
        view.append([top_pair])
        if middlepairs:
            view += regroup_list(middlepairs, MIDDLE_PAIR_GROUPING)
    else:
        if middlepairs:
            view += regroup_list(middlepairs, MIDDLE_PAIR_GROUPING)
        view.append([top_pair])

    # other 1 pair intersections
    if rank_count_list[0][1:]:
        view.append(rank_count_list[0][1:])

    return view


def paired_board_made(board):
    view = []
    rank_count_list = board_util.return_rank_counts(board)

    intersections = board_util.hand_board_intersections(board)
    kickers = board_util.return_kickers(board)

    # str flushes
    view.append(board_util.return_str_flushes(board))
    # full or better
    view += regroup_list(board_util.return_fulls_or_better(board),
                         PAIRED_BOARD_FULL_OR_BETTER_GROUPING)

    flushes = board_util.return_flushes(board)
    straights = board_util.return_straights(board)

    if flushes:
        view += (regroup_list(flushes, FLUSH_GROUPING))
        if straights[0]:
            view.append(straights[0] + straights[1])
    elif straights[0]:
        view.append(straights[0])
        if straights[1]:
            view.append(straights[1])
        if straights[2]:
            view.append(straights[2])

    if not flushes and not straights[0]:
        view.append([kickers[0] + intersections[0]])
        view.append([kickers[1] + intersections[0],
                     kickers[2] + intersections[0]])

    view.append([intersections[0]])

    # add undertrips if possible
    if len(rank_count_list[1]) >= 2:
        view.append(rank_count_list[1][1])

    overpairs = board_util.return_over_pairs(board)
    middlepairs = board_util.return_middle_pairs(board)

    if len(rank_count_list[0]) != 0:
        top_pair = rank_count_list[0][0]
    else: # turn double paired board
        top_pair = board_util.return_pairs(board)[0][0] # just use highcard :-(...might give bad results

    if overpairs:
        view += regroup_list(overpairs, OVERPAIR_GROUPING)

    # top pair
    # middle pairs
    if RANK_ORDER[top_pair] > RANK_ORDER[rank_count_list[1][0]]:
        view.append([top_pair])
        if middlepairs:
            view += regroup_list(middlepairs, MIDDLE_PAIR_GROUPING)
    else:
        if middlepairs:
            view += regroup_list(middlepairs, MIDDLE_PAIR_GROUPING)
        view.append([top_pair])
    # other 1 pair intersections
    if rank_count_list[0][1:]:
        view.append(rank_count_list[0][1:])

    return view


def paired_board_draw(board):
    view = []

    fd_1, fd_2 = board_util.return_flushdraws(board)
    straight_draws = board_util.return_straight_draws(board)

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd = [fd_1[0]]
        fd = [fd_1[0][1:]]
        if fd_2:
            nfd.append(fd_2[0])
            fd.append(fd_2[0][1:])
        # nfd no decent sd value
        view.append(nfd)
        # bare fd
        view.append(fd)

    if straight_draws["gs"]:
        # better straight draws
        if straight_draws["oesd"]:
            view.append(straight_draws["wraps"] + straight_draws["oesd"])
        # gs draws
        view.append(straight_draws["gs"])
    return view


def paired_board_blocker(board):
    view = []
    blockers = board_util.return_full_blockers(board)

    # str flush blockers
    if board_util.return_str_flushes(board) != []:
        str_flushes = board_util.return_str_flushes(board)
        str_flush_blockers = []
        for str_flush in str_flushes:
            str_flush_blockers.append(str_flush[0:2])
            str_flush_blockers.append(str_flush[2:4])
            str_flush_blockers=list(set(str_flush_blockers))
        view += regroup_list(str_flush_blockers,[1,1,1])

    # 2 baord pair blockers
    view.append([hand for hand in blockers if len(hand) == 2])

    # pair blockers
    view += regroup_list([hand for hand in blockers if len(hand)
                          == 1], PAIR_GROUPING)

    # flush blockers
    f_blocker = board_util.return_flush_blockers(board)
    if f_blocker:
        view.append([f_blocker[0]])
        view.append([f_blocker[2], f_blocker[3]])
    str_blocker = board_util.return_straight_blocker_pairs(board)
    if str_blocker:
        view.append(str_blocker)

    fd_1, fd_2 = board_util.return_flushdraws(board)

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd_blocker = [fd_1[0][:2]]
        fd_blocker = [fd_1[0][1]]
        if fd_2:
            nfd_blocker.append(fd_2[0][:2])
            fd_blocker.append(fd_2[0][1])
        view.append(nfd_blocker)
        view.append(fd_blocker)
    return view


def flush_board(board):
    flushes = board_util.return_flushes(board)
    flush_blockers = board_util.return_flush_blockers(board)
    str_draws = board_util.return_straight_draws(board)
    overpairs = board_util.return_over_pairs(board)

    view = []

    # str flushes
    view.append(board_util.return_str_flushes(board))

    # flushes
    view += regroup_list(flushes, FLUSH_GROUPING)

    made_hands = regroup_board_intersections(board)

    # sets
    view += regroup_list(made_hands["sets"], SET_GROUPING)

    # straights
    straights = board_util.return_straights(board)
    for s in straights:
        if s:
            view.append(s)

    # 2 pair
    view.append(made_hands["top2"])
    view.append(made_hands["topbottom"])
    view.append(made_hands["random2"])

    # flush blocker
    view.append([flush_blockers[0]])
    view.append([flush_blockers[1]])

    # oesd or better
    if str_draws:
        view.append(str_draws["wraps"] + str_draws["oesd"])

    # op or tp with or without flushblocker
    view.append([[flushes[0][1]], overpairs[0:2] + [made_hands["pair"][0]]])
    view.append(overpairs[0:2] + [made_hands["pair"][0]])

    # random flushblocker
    view.append([flushes[0][1]])

    return view


def flush_board_made(board):
    flushes = board_util.return_flushes(board)
    overpairs = board_util.return_over_pairs(board)

    view = []

    # str flushes
    view.append(board_util.return_str_flushes(board))

    # flushes
    view += regroup_list(flushes, FLUSH_GROUPING)

    made_hands = regroup_board_intersections(board)

    # sets
    view += regroup_list(made_hands["sets"], SET_GROUPING)

    # straights
    straights = board_util.return_straights(board)
    for s in straights:
        if s:
            view.append(s)

    # 2 pair
    view.append(made_hands["top2"])
    view.append(made_hands["topbottom"])
    view.append(made_hands["random2"])

    # op or tp
    view.append(overpairs[0:2] + [made_hands["pair"][0]])
    return view


def flush_board_draw(board):
    str_draws = board_util.return_straight_draws(board)
    view = []
    # oesd or better
    if str_draws:
        view.append(str_draws["wraps"])
        view.append(str_draws["oesd"])
        view.append(str_draws["gs"])
    return view


def flush_board_blocker(board):
    view = []

    flush_blockers = board_util.return_flush_blockers(board)

    # flush blocker
    view += regroup_list(flush_blockers, FLUSH_GROUPING)
    return view


def straight_board(board):
    view = []
    fd_1, fd_2 = board_util.return_flushdraws(board)
    straight_draws = board_util.return_straight_draws(board)
    straights = board_util.return_straights(board)

    made_hands = regroup_board_intersections(board)
    overpairs = board_util.return_over_pairs(board)
    blockerpairs = board_util.return_straight_blocker_pairs(board)
    overpairs = [pair for pair in overpairs if pair not in blockerpairs]

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd = [fd_1[0]]
        fd = [fd_1[0][1:]]
        if fd_2:
            nfd.append(fd_2[0])
            fd.append(fd_2[0][1:])

        # nut or 2nd straight + fd or set
        view.append([straights[0] + straights[1], fd + made_hands["sets"]])
        # sets + fd
        view.append([fd, made_hands["sets"]])
    else:
        # nut or 2nd striaght + >top2
        view.append([straights[0] + straights[1],
                     made_hands["sets"] + made_hands["top2"]])

    # straights bare
    for s in straights:
        if s:
            view.append(s)

    # sets + 1 nutstraight card
    view.append([made_hands["sets"], [p[0] for p in blockerpairs]])
    # sets
    view += regroup_list(made_hands["sets"], SET_GROUPING)
    if fd_1 and len(board_util.return_ranks(board)) != 5:
        # 2 pair + fd
        view.append([fd, made_hands["top2"] +
                     made_hands["topbottom"] + made_hands["random2"]])
        # nfd + wrap, oesd and better gs
        view.append([nfd,
                     straight_draws["wraps"] +
                     straight_draws["oesd"] +
                     straight_draws["gs"][:int(len(straight_draws["gs"]) // 1.5)]])
        # fd + wrap, oesd and better gs draw
        view.append([fd, straight_draws["wraps"] +
                     straight_draws["oesd"] +
                     straight_draws["gs"][:int(len(straight_draws["gs"]) // 1.5)]])
        # fd + blockerpairs
        view.append([fd, blockerpairs])
        # nfd bare
        view.append(nfd)
        # fd bare
        view.append(fd)

    # top2 and topbottom + 1 blocker
    view.append([made_hands["top2"] + made_hands["topbottom"],
                 [p[0] for p in blockerpairs]])
    view.append(made_hands["top2"])
    view.append(made_hands["topbottom"])
    view.append(made_hands["random2"])

    # nut straightblockers
    view.append(blockerpairs)

    # overpairs,tp + gs+ draws
    view.append([overpairs + [made_hands["pair"][0]],
                 straight_draws["wraps"] +
                 straight_draws["oesd"] +
                 straight_draws["gs"][:int(len(straight_draws["gs"]) // 1.5)]])
    # overpairs
    if overpairs:
        view += regroup_list(overpairs, OVERPAIR_GROUPING)
    # oesd+ draws
    if straight_draws["oesd"]:
        view.append(straight_draws["wraps"] +
                    straight_draws["oesd"])
    # gs
    view.append(straight_draws["gs"])

    # top pair
    view.append(made_hands["pair"][0])

    # 1 str blocker
    view.append([p[0] for p in blockerpairs])

    return view


def straight_board_made(board):
    view = []
    straights = board_util.return_straights(board)

    made_hands = regroup_board_intersections(board)
    overpairs = board_util.return_over_pairs(board)

    # straights bare
    for s in straights:
        if s:
            view.append(s)

    # sets
    view += regroup_list(made_hands["sets"], SET_GROUPING)

    # top2 and topbottom

    view.append(made_hands["top2"])
    view.append(made_hands["topbottom"])
    view.append(made_hands["random2"])

    # overpairs
    if overpairs:
        view += regroup_list(overpairs, OVERPAIR_GROUPING)

    # top pair
    view.append(made_hands["pair"][0])
    return view


def straight_board_draw(board):
    view = []
    fd_1, fd_2 = board_util.return_flushdraws(board)
    straight_draws = board_util.return_straight_draws(board)

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd = [fd_1[0]]
        fd = [fd_1[0][1:]]
        if fd_2:
            nfd.append(fd_2[0])
            fd.append(fd_2[0][1:])
        # nfd bare
        view.append(nfd)
        # fd bare
        view.append(fd)

    # oesd+ draws
    if straight_draws["wraps"]:
        view.append(straight_draws["wraps"])
    if straight_draws["oesd"]:
        view.append(straight_draws["oesd"])

    # gs
    view.append(straight_draws["gs"])
    return view


def straight_board_blocker(board):
    view = []
    fd_1, fd_2 = board_util.return_flushdraws(board)
    blockerpairs = board_util.return_straight_blocker_pairs(board)

    # nut straightblockers
    view.append(blockerpairs)

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd_blocker = [fd_1[0][:2]]
        fd_blocker = [fd_1[0][1]]
        if fd_2:
            nfd_blocker.append(fd_2[0][:2])
            fd_blocker.append(fd_2[0][1])
        view.append(nfd_blocker)
        view.append(fd_blocker)

    # 1 str blocker
    view.append([p[0] for p in blockerpairs])

    return view


def std_board(board):
    view = []
    fd_1, fd_2 = board_util.return_flushdraws(board)
    straight_draws = board_util.return_straight_draws(board)
    made_hands = regroup_board_intersections(board)
    overpairs = board_util.return_over_pairs(board)

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd = [fd_1[0]]
        secnfd = [fd_1[1]]
        fd = [fd_1[0][1:]]
        if fd_2:
            nfd.append(fd_2[0])
            secnfd.append(fd_2[1])
            fd.append(fd_2[0][1:])
        nfd_blocker = [i[:2] for i in nfd]
        secnfd_blocker = [i[:2] for i in secnfd]
        # sets + fd
        view.append([fd, made_hands["sets"]])
        # top2, topbottom + fd
        view.append([fd, made_hands["top2"] + made_hands["topbottom"]])

        # nfd + any 2, tp, nut 2 overpair
        view.append([nfd, made_hands["random2"] +
                     [made_hands["pair"][0]] + overpairs[:2]])
        # nfd + oesd and better half of gs
        if straight_draws["gs"]:
            view.append([nfd, straight_draws["wraps"] +
                         straight_draws["oesd"] +
                         straight_draws["gs"][:int(len(straight_draws["gs"]) // 1.5)]])
        # nfd
        view.append(nfd)
        # fd + any 2, tp, oesd and better half of gs  draws
        if straight_draws["gs"]:
            view.append([fd, made_hands["random2"] +
                         [made_hands["pair"][0]] +
                         straight_draws["wraps"] +
                         straight_draws["oesd"] +
                         straight_draws["gs"][:int(len(straight_draws["gs"]) // 1.5)]])
        else:
            view.append([fd, made_hands["random2"] + [made_hands["pair"][0]]])
        # fd + op
        view.append([fd, overpairs])
        # fd
        view.append(fd)
    # set, top 2 + str draws
    if straight_draws["gs"]:
        view.append([made_hands["sets"] + made_hands["top2"],
                     straight_draws["wraps"] +
                     straight_draws["oesd"] +
                     straight_draws["gs"][:int(len(straight_draws["gs"]) // 1.5)]])
    # set
    view += regroup_list(made_hands["sets"], SET_GROUPING)
    # top 2
    view.append(made_hands["top2"])
    # top bottom
    view.append(made_hands["topbottom"])
    # any 2
    view.append(made_hands["random2"])

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        # nfd_blocker + sd value
        view.append([nfd_blocker, overpairs + made_hands["pair"][:1]])
        # nfd_blocker + oesd + str draw
        if straight_draws["gs"]:
            view.append([nfd_blocker,
                         straight_draws["wraps"] +
                         straight_draws["oesd"]])
        # nfd_blocker bare
        view.append(nfd_blocker)
        # 2nfd blocker overall
        view.append(secnfd_blocker)

    if straight_draws["gs"]:
        # op, tp + oesd draw
        view.append([overpairs + made_hands["pair"][:1],
                     straight_draws["wraps"] +
                     straight_draws["oesd"]])
        # op, tp + gs
        view.append([overpairs + made_hands["pair"][:1],
                     straight_draws["gs"]])
        # str draw bare
        view.append(straight_draws["wraps"])
        view.append(straight_draws["oesd"])
        view.append(straight_draws["gs"])
    # op bare
    view += regroup_list(overpairs, OVERPAIR_GROUPING)
    # board pairs
    view += regroup_list(made_hands["pair"], PAIR_GROUPING)
    # middlepairs
    if board_util.return_middle_pairs(board):
        view += regroup_list(board_util.return_middle_pairs(board), MIDDLE_PAIR_GROUPING)
    return view


def std_board_made(board):
    view = []
    made_hands = regroup_board_intersections(board)
    overpairs = board_util.return_over_pairs(board)

    # set
    view += regroup_list(made_hands["sets"], SET_GROUPING)
    # top 2
    view.append(made_hands["top2"])
    # top bottom
    view.append(made_hands["topbottom"])
    # any 2
    view.append(made_hands["random2"])
    # op bare
    view += regroup_list(overpairs, OVERPAIR_GROUPING)
    # board pairs
    view += regroup_list(made_hands["pair"], PAIR_GROUPING)
    # middlepairs
    if board_util.return_middle_pairs(board):
        view += regroup_list(board_util.return_middle_pairs(board), MIDDLE_PAIR_GROUPING)
    return view


def std_board_draw(board):
    view = []
    fd_1, fd_2 = board_util.return_flushdraws(board)
    straight_draws = board_util.return_straight_draws(board)

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd = [fd_1[0]]
        fd = [fd_1[0][1:]]
        if fd_2:
            nfd.append(fd_2[0])
            fd.append(fd_2[0][1:])
        # nfd bare
        view.append(nfd)
        # fd bare
        view.append(fd)

    # oesd+ draws
    if straight_draws["wraps"]:
        view.append(straight_draws["wraps"])
    if straight_draws["oesd"]:
        view.append(straight_draws["oesd"])

    # gs
    if straight_draws["gs"]:
        view.append(straight_draws["gs"])
    return view


def std_board_blocker(board):
    view = []
    fd_1, fd_2 = board_util.return_flushdraws(board)
    straight_draws = board_util.return_straight_draws(board)
    made_hands = regroup_board_intersections(board)

    # fd blockers
    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd_blocker = [fd_1[0][:2]]
        secnd_blocker = [fd_1[1][:2]]
        fd_blocker = [fd_1[0][1]]
        if fd_2:
            nfd_blocker.append(fd_2[0][:2])
            secnd_blocker = [fd_2[1][:2]]
            fd_blocker.append(fd_2[0][1])
        view.append(nfd_blocker)
        view.append(secnd_blocker)
        view.append(fd_blocker)

    # pair blockers
    view += regroup_list(made_hands["pair"], PAIR_GROUPING)

    # str draw blockers
    if straight_draws["wraps"]:
        str_blockers = [i * 2 for i in straight_draws["wraps"][0]]
        view.append(str_blockers)
    return view


def custom_view(board):
    # TODO
    view = []
    made_hands = regroup_board_intersections(board)
    entry = made_hands["sets"] + made_hands["top2"] + made_hands["topbottom"] + made_hands["random2"]
    view.append(entry)
    overpairs = board_util.return_over_pairs(board)
    # view+=regroup_list(overpairs,OVERPAIR_GROUPING)
    view.append([made_hands["pair"][0]])
    return view

def flush_suits(board):
    view = []

    flop_board = board[0:3]+[RANDOM_CARD,RANDOM_CARD]
    turn_board = board[0:4]+[RANDOM_CARD]
    flop_flushes = board_util.return_flushes(flop_board)
    flop_fd, _ = board_util.return_flushdraws(flop_board)
    flop_fd_blocker = [x[0:2] for x in flop_fd]
    flop_bd_suits = [s for c,s in board_util.return_suits(flop_board) if c == 1]
    flop_bd_fd = [[],[],[]]
    for i in range(0,len(flop_bd_suits)):
      flop_bd_fd[i]=[r + flop_bd_suits[i] * 2 for r in board_util.possible_flush_or_fd_ranks(flop_board, flop_bd_suits[i])]
    turn_flushes = board_util.return_flushes(turn_board)
    turn_fds = board_util.return_flushdraws(turn_board)
    turn_fd = []
    for fd in turn_fds:
        if fd:
            if flop_fd:
                if fd[0][1] != flop_fd[0][1]:
                    turn_fd = fd
            else:
                turn_fd = fd
    turn_fd_blocker = [x[0:2] for x in turn_fd]
    river_flushes = board_util.return_flushes(board)

    # start @ river and go from there back:
    if river_flushes and not turn_flushes:
        view+=regroup_list(river_flushes,FLUSH_GROUPING)
        view+=regroup_list(board_util.return_flush_blockers(board),FLUSH_GROUPING)
        if fd and fd[0][1] != river_flushes[0][1]:
            view+=regroup_list(fd,FD_GROUPING)
        return view
    if turn_flushes:
        view+=regroup_list(turn_flushes,FLUSH_GROUPING)
        view+=regroup_list(board_util.return_flush_blockers(turn_board),FLUSH_GROUPING)
        for bd_fd in flop_bd_fd:
            if bd_fd and bd_fd[0][1] != turn_flushes[0][1]:
                view+=regroup_list(bd_fd, BD_FD_GROUPING)
        return view
    if flop_fd and turn_fd: #double fd
        view+= [[flop_fd[-1][1:]+turn_fd[-1][1:]]]
    if flop_fd:
        view+=regroup_list(flop_fd,FD_GROUPING)
    if turn_fd:
        view+=regroup_list(turn_fd,FD_GROUPING)
    if flop_fd_blocker:
        view+=regroup_list(flop_fd_blocker,FD_BLOCKER_GROUPING)
    if turn_fd_blocker:
        view+=regroup_list(turn_fd_blocker,FD_BLOCKER_GROUPING)
    bd_suits = []
    for bd_fd in flop_bd_fd:
        if bd_fd:
            if turn_fd:
                if bd_fd[0][1] != turn_fd[0][1]:
                    bd_suits.append(bd_fd[0][1]*2)
            else:
                bd_suits.append(bd_fd[0][1]*2)
    if len(bd_suits) > 1:
        bd_double_fd = itertools.combinations(bd_suits,2)
        bd_d_fd = [''.join(x) for x in bd_double_fd]
        view+=[bd_d_fd]
    for bd_fd in flop_bd_fd:
        if bd_fd:
            if turn_fd:
                if bd_fd[0][1] != turn_fd[0][1]:
                    view+=regroup_list(bd_fd,BD_FD_GROUPING)
            else:
                view+=regroup_list(bd_fd,BD_FD_GROUPING)
    return view

def straight_draw_view(board):
    straights = board_util.return_straights(board)
    str_blocker_pairs = board_util.return_straight_blocker_pairs(board)
    str_blockers = [x[0] for x in str_blocker_pairs]

    view = []

    if straights[0]:
        for str in straights:
            if str:
                view.append(str)
        view+=regroup_list(str_blocker_pairs,[1,1,1,1])
        view+=regroup_list(str_blockers,[1,1,1,1])

    turn_board = board[0:4]+[RANDOM_CARD]
    draws = board_util.return_straight_draws(turn_board)
    view+=regroup_list(draws["wraps"],STR_DRAW_GROUPING)
    view+=regroup_list(draws["oesd"],STR_DRAW_GROUPING)
    view+=regroup_list(draws["gs"],STR_DRAW_GROUPING)

    if not straights[0]:
        str_draws = draws
        if str_draws["gs"]:
            str_draws = clean([str_draws["wraps"]+str_draws["oesd"]+str_draws["gs"]])[0]
            str_draws = list("".join(str_draws))
            str_draw_counts = [[], [], [], [], []]
            for i in range(0, 5):
                str_draw_counts[i] = list(set(r for r in str_draws if str_draws.count(r) == (i + 1)))
            for i in str_draw_counts:
                i.sort(key=lambda x: RANK_ORDER[x], reverse=True)
            for i in range(4,1,-1):
                view+=regroup_list(str_draw_counts[i],[1,1,1,1])

    view = clean(view)
    ret_view = []
    [ret_view.append(x) for x in view if x not in ret_view]
    return ret_view


def pair_view(board):
    pairs = board_util.return_pairs(board)
    view = regroup_list(pairs, POCKET_PAIR_GROUPING)
    return view


def board_interaction_view(board):
    fulls = board_util.return_fulls_or_better(board)
    intersections = board_util.hand_board_intersections(board)
    all_combos = fulls + intersections
    view = regroup_list(all_combos,BOARD_INTERACTION_GROUPING)
    return view

def relevant_hole_cards(board):
    flop_board = board[0:3]+[RANDOM_CARD,RANDOM_CARD]
    turn_board = board[0:4]+[RANDOM_CARD]
    flop_fd, _ = board_util.return_flushdraws(flop_board)
    flop_fd_blocker = [x[0:2] for x in flop_fd]
    turn_fds = board_util.return_flushdraws(turn_board)
    turn_fd = []
    for fd in turn_fds:
        if fd:
            if flop_fd:
                if fd[0][1] != flop_fd[0][1]:
                    turn_fd = fd
            else:
                turn_fd = fd
    turn_fd_blocker = [x[0:2] for x in turn_fd]

    # board interactions
    rank_count = board_util.return_rank_counts(board)
    rank_view = []
    for i in range(2,-1,-1):
        if rank_count[i]:
            rank_view += [[x] for x in rank_count[i]]

    # flush blockers
    flush_blockers = board_util.return_flush_blockers(board)
    flush_view=regroup_list(flush_blockers,[1,1,1,1])

    # straight blockers
    blockerpairs = board_util.return_straight_blocker_pairs(board)
    straight_view=regroup_list([b[0] for b in blockerpairs], [1,1,1,1])

    if rank_count[3] != [] or rank_count[2] != [] or rank_count[1] != []:
        view = rank_view+flush_view+straight_view
    else:
        view = flush_view+straight_view+rank_view

    # flop fd blockers
    if flop_fd_blocker:
        if flush_blockers:
            if flush_blockers[0][1] != flop_fd_blocker[0][1]:
                view+=regroup_list(flop_fd_blocker,[1,1,1,1])
        else:
            view+=regroup_list(flop_fd_blocker,[1,1,1,1])

    # turn fd blockers
    if turn_fd_blocker:
        if flush_blockers:
            if flush_blockers[0][1] != turn_fd_blocker[0][1]:
                view+=regroup_list(turn_fd_blocker,[1,1,1,1])
        else:
            view+=regroup_list(turn_fd_blocker,[1,1,1,1])

    # straight draw blockers

    str_draws = board_util.return_straight_draws(turn_board)
    if str_draws["gs"]:
        str_draws = clean([str_draws["wraps"]+str_draws["oesd"]+str_draws["gs"]])[0]
        str_draws = list("".join(str_draws))
        str_draw_counts = [[], [], [], [], []]
        for i in range(0, 5):
            str_draw_counts[i] = list(set(r for r in str_draws if str_draws.count(r) == (i + 1)))
        for i in str_draw_counts:
            i.sort(key=lambda x: RANK_ORDER[x], reverse=True)
        for i in range(4,1,-1):
            view+=regroup_list(str_draw_counts[i],[1,1,1,1])
    # kickers
    if len(view) < 10:
        kickers = board_util.return_kickers(board)
        kickers = kickers[:4]
        view+= regroup_list(kickers,[1,1,1,1])

    view = clean(view)
    ret_view = []
    [ret_view.append(x) for x in view if x not in ret_view]
    return ret_view

def clean(view):
    new_view = []
    for item in view:
        if len(item) == 0:  # discard empty view entry
            continue
        if item in new_view:
            continue
        if type(item[0]) != list:  # standard view entry -> list of strings
            new_view.append(board_util.compact_range(item))
        elif len(item[0]) != 0 and len(item[1]) != 0:  # discard emtpy view entry
            new_view.append([board_util.compact_range(i) for i in item])
    return new_view


def combine_views(board, view_type_1, view_type_2, ignore_first_entry=True):
    view_1 = get_view(board, view_type_1)
    view_2 = get_view(board, view_type_2)

    views = []
    megaview = []

    # test if there are no combined entries
    for item in view_1:
        for entry in item:
            if type(entry) == list:
                logging.error("Combine VIEW doesnt support views with : entries")
                return views.append(view_1)  # just return 1 view (the first one)
    for item in view_2:
        for entry in item:
            if type(entry) == list:
                logging.error("Combine VIEW doesnt support views with : entries")
                return views.append(view_1)  # just return 1 view (the first one)

    top_entry = []
    if ignore_first_entry:
        # views.append(view_1[0])
        megaview.append(view_1[0])
        top_entry += view_1[0]
        view_1 = view_1[1:]

    for view_1_entry in view_1:
        view = [top_entry]
        for view_2_entry in view_2:
            view.append([view_1_entry, view_2_entry])
            megaview.append([view_1_entry, view_2_entry])
        view.append(view_1_entry)
        megaview.append(view_1_entry)
        view = clean(view)
        views.append(view)
        top_entry += view_1_entry
    view = [top_entry]
    for view_2_entry in view_2:
        view.append(view_2_entry)
        megaview.append(view_2_entry)
    view = clean(view)
    views.append(view)
    megaview = clean(megaview)
    return views, megaview


def get_view(board_str, view_type):
    board = board_util.parse_board(board_str)
    if view_type == "DRAWS": # if river return turn draw view
        board = board[0:4]+[RANDOM_CARD]
    rank_count_list = board_util.return_rank_counts(board)

    if view_type == "DEFAULT":
        if rank_count_list[3] != []:
            return clean(quad_board(board))
        if rank_count_list[2] != []:
            return clean(trips_board(board))
        if rank_count_list[1] != []:
            return clean(paired_board(board))
        if board_util.return_flushes(board):
            return clean(flush_board(board))
        if board_util.return_straights(board)[0]:
            return clean(straight_board(board))
        return clean(std_board(board))
    elif view_type == "MADE_HANDS":
        if rank_count_list[3] != []:
            return clean(quad_board(board))
        if rank_count_list[2] != []:
            return clean(trips_board(board))
        if rank_count_list[1] != []:
            return clean(paired_board_made(board))
        if board_util.return_flushes(board):
            return clean(flush_board_made(board))
        if board_util.return_straights(board)[0]:
            return clean(straight_board_made(board))
        return clean(std_board_made(board))
    elif view_type == "DRAWS":
        if rank_count_list[3] != []:
            return []
        if rank_count_list[2] != []:
            return []
        if rank_count_list[1] != []:
            return clean(paired_board_draw(board))
        if board_util.return_flushes(board):
            return clean(flush_board_draw(board))
        if board_util.return_straights(board)[0]:
            return clean(straight_board_draw(board))
        return clean(std_board_draw(board))
    elif view_type == "BLOCKERS":
        if rank_count_list[3] != []:
            return []
        if rank_count_list[2] != []:
            return clean(trips_board_blocker(board))
        if rank_count_list[1] != []:
            return clean(paired_board_blocker(board))
        if board_util.return_flushes(board):
            return clean(flush_board_blocker(board))
        if board_util.return_straights(board)[0]:
            return clean(straight_board_blocker(board))
        return clean(std_board_blocker(board))
    elif view_type == "CUSTOM":
        return clean(custom_view(board))
    elif view_type == "DRAWS_BLOCKERS":
        return clean(get_view(board_str, "DRAWS") + get_view(board_str, "BLOCKERS"))
    elif view_type == "FLUSH":
        return clean(flush_suits(board))
    elif view_type == "STRAIGHT":
        return clean(straight_draw_view(board))
    elif view_type == "POCKET_PAIRS":
        return clean(pair_view(board))
    elif view_type == "BOARD_RANKS":
        return clean(board_interaction_view(board))
    elif view_type == "KEY_CARDS":
        return clean(relevant_hole_cards(board))
    print("Unsupported VIEW TYPE: {}".format(view_type))
    return []


def view_item_to_str(item):
    if not item:
        return ""
    if type(item) == str:
        return item
    string = ""
    if type(item[0]) == str:
        for i in item:
            string += i + ","
        string = string[:-1]
    elif type(item[0]) == list and len(item) == 2:
        string1 = ""
        for i in item[0]:
            string1 += i + ","
        string1 = "(" + string1[:-1] + "):"
        string2 = ""
        for i in item[1]:
            string2 += i + ","
        string2 = "(" + string2[:-1] + ")"
        string = string1 + string2
    return string

def expand_range(hand,board_str):
    """
    returns string with all + expressions replaced
    """
    board = board_util.parse_board(board_str)
    ranks=board_util.return_ranks(board)
    flushes=board_util.return_flushes(board)
    straights=board_util.return_straights(board)
    straights=[j for i in straights for j in i]
    fulls_or_better=board_util.return_fulls_or_better(board)
    hand_board_int=board_util.hand_board_intersections(board)
    str_draw_classes=board_util.return_straight_draws(board)
    str_draws = str_draw_classes["wraps"]+str_draw_classes["oesd"]+str_draw_classes["gs"]
    kickers=board_util.return_kickers(board)
    pairs=board_util.return_pairs(board)

    flush_suit=[]
    if flushes:
        flush_suit= flush_suit + [flushes[0][1:]]
    str_flush=board_util.return_str_flushes(board)

    match_expr=re.compile('['+''.join(RANKS)+']'+'{3,4}'+'\+') #start with longest possible expressions == 3, 4 card wraps
    hand_sections=match_expr.findall(hand)

    if hand_sections:
        for x in hand_sections:
            compare_x = ''.join(sorted(x[:-1], key=lambda x:RANK_ORDER[x], reverse=True))
            if compare_x in str_draws:
                replace_hands=str_draws[0:str_draws.index(compare_x)+1] # all better draws including written hand
                replace_hands=board_util.compact_range(replace_hands)
                hand=hand.replace(x,view_item_to_str(replace_hands))

    match_expr=re.compile('['+''.join(RANKS)+']'+'['+''.join(SUITS)+']'+'{1,2}'+'\+') #flush flushdraw or blocker
    hand_sections=match_expr.findall(hand)

    if hand_sections:
       for x in hand_sections:
           compare_x=x[0:-1]
           if len(compare_x) == 2: # can only be blocker...todo exclude flushes? add !suit suit
               flush_blocker=board_util.return_flush_blockers(board)
               if compare_x in flush_blocker:
                   replace_hands=flush_blocker[0:flush_blocker.index(compare_x)+1]
                   replace_hands=board_util.compact_range(replace_hands)
                   hand=hand.replace(x,view_item_to_str(replace_hands))
           else: # flush or flushdraw
               if flushes:
                   flushes=board_util.return_flushes(board)
                   if compare_x in flushes:
                       replace_hands=fulls_or_better + flushes[0:flushes.index(compare_x)+1]
                       replace_hands=board_util.compact_range(replace_hands)
                       hand=hand.replace(x,view_item_to_str(replace_hands))
                   else:
                       flush_drw=board_util.return_flushdraws(board,compare_x[-1])
                       if flush_drw:
                           replace_hands=flush_drw[0:flush_drw.index(compare_x)+1]
                           replace_hands=board_util.compact_range(replace_hands)
                           hand=hand.replace(x,view_item_to_str(replace_hands))

    match_expr=re.compile('['+''.join(RANKS)+']'+'{2}'+'\+') #straights, str draws or hand board intersections
    hand_sections=match_expr.findall(hand)

    if hand_sections:
        for x in hand_sections:
            compare_x=''.join(sorted(x[:-1], key=lambda x:RANK_ORDER[x], reverse=True))

            if compare_x in fulls_or_better:
                replace_hands=str_flush+fulls_or_better[0:fulls_or_better.index(compare_x)+1]
                replace_hands=board_util.compact_range(replace_hands)
                hand=hand.replace(x,view_item_to_str(replace_hands))
            elif compare_x in straights:
                replace_hands=str_flush+fulls_or_better+flush_suit+straights[0:straights.index(compare_x)+1]
                replace_hands=board_util.compact_range(replace_hands)
                hand=hand.replace(x,view_item_to_str(replace_hands))
            elif compare_x in str_draws:
                replace_hands=str_draws[0:str_draws.index(compare_x)+1]
                replace_hands=board_util.compact_range(replace_hands)
                hand=hand.replace(x,view_item_to_str(replace_hands))
            elif compare_x in hand_board_int:
                replace_hands=str_flush+fulls_or_better+flush_suit+straights+hand_board_int[0:hand_board_int.index(compare_x)+1]
                replace_hands=board_util.compact_range(replace_hands)
                hand=hand.replace(x,view_item_to_str(replace_hands))
            elif x[1] in hand_board_int: # pair + kicker?
                replace_hands=hand_board_int[0:hand_board_int.index(x[1])]
                better_kickers=kickers[0:kickers.index(x[0])+1]
                replace_hands=str_flush+fulls_or_better+flush_suit+straights+replace_hands+[k+x[1] for k in better_kickers]
                replace_hands=board_util.compact_range(replace_hands)
                hand=hand.replace(x,view_item_to_str(replace_hands))
            elif compare_x in pairs: # pocket pairs...only add pair or better
                replace_hands=pairs[0:pairs.index(compare_x)+1]
                replace_hands=board_util.compact_range(replace_hands)
                hand=hand.replace(x,view_item_to_str(replace_hands))

    match_expr=re.compile('['+''.join(RANKS)+']'+'{1}'+'\+') #one pair or better
    hand_sections=match_expr.findall(hand)

    if hand_sections:
        for x in hand_sections:
            compare_x=x[:-1]
            if compare_x in hand_board_int:
                replace_hands=str_flush+fulls_or_better+flush_suit+straights+hand_board_int[0:hand_board_int.index(compare_x)+1]
                replace_hands=board_util.compact_range(replace_hands)
                hand=hand.replace(x,view_item_to_str(replace_hands))

    match_expr=re.compile('['+''.join(LOW_CARDS)+']'+'{2}'+'\<') #find HILO hand with < at the end
    hand_sections=match_expr.findall(hand)

    if hand_sections:
        low_hands=board_util.return_lows(ranks)
        for x in hand_sections:
            compare_x=x[:-1]
            if compare_x in low_hands:
                replace_hands=low_hands[0:low_hands.index(compare_x)+1]
                replace_hands=board_util.compact_range(replace_hands)
                hand=hand.replace(x,view_item_to_str(replace_hands))
    if '+' in hand:
        logging.error("Could not resolve one or more + expressions in hand:\n{0}".format(hand))
        return ""
    if '<' in hand:
        logging.error("Could not resolve one or more < expressions in hand:\n{0}".format(hand))
        return ""
    return hand

def print_view(view, view_type=VIEW_TYPES[0], view_folder=VIEW_FOLDER, filename=DEFAULT_VIEW_NAME):
    if filename:
        filename = filename + "-" + view_type + ".txt"
    else:
        filename = view_type + ".txt"
    filename = os.path.join(view_folder, filename)
    with open(filename, "w") as f:
        f.write(TOP_VIEW_LINE)
        f.write("\n")
        for item in view:
            string = view_item_to_str(item) + "\n"
            f.write(string)
            f.write(string)
            f.write("\n")


def try_it():
    board_string = "2d4c8d5cKc"
    for iterations in range(0,10):
        num_cards = random.randint(3,5)
        board_string = "".join(random.sample(CARDS,num_cards))
        #board_string = "2d4c8c"
        board = board_util.parse_board(board_string)
        view_default = get_view(board_string, VIEW_TYPES[0])
        view_made = get_view(board_string, VIEW_TYPES[1])
        view_draws = get_view(board_string, VIEW_TYPES[2])
        view_blockers = get_view(board_string, VIEW_TYPES[3])
        view_draws_blockers=get_view(board_string,VIEW_TYPES[4])
        view_flush = get_view(board_string,VIEW_TYPES[5])
        view_straight = get_view(board_string, VIEW_TYPES[6])
        view_board_rank = get_view(board_string, VIEW_TYPES[7])
        view_key_cards = get_view(board_string, VIEW_TYPES[8])
        view_pocket = get_view(board_string, VIEW_TYPES[9])

        print("DEFAULT_VIEW FOR BOARD:{}".format(board_string))
        for item in view_default:
            print(item)
        print("MADE_VIEW FOR BOARD:{}".format(board_string))
        for item in view_made:
            print(item)
        print("DRAW_VIEW FOR BOARD:{}".format(board_string))
        for item in view_draws:
            print(item)
        print("BLOCKER_VIEW FOR BOARD:{}".format(board_string))
        for item in view_blockers:
            print(item)
        print("DRAW_BLOCKER_VIEW FOR BOARD:{}".format(board_string))
        for item in view_draws_blockers:
            print(item)
        print("FLUSH_SUIT_VIEW FOR BOARD:{}".format(board_string))
        for item in view_flush:
            print(item)
        print("STR_DRAW_VIEW FOR BOARD:{}".format(board_string))
        for item in view_straight:
            print(item)
        print("BOARD RANK FOR BOARD:{}".format(board_string))
        for item in view_board_rank:
            print(item)
        print("KEY CARDS FOR BOARD:{}".format(board_string))
        for item in view_key_cards:
            print(item)
        print("POCKETS FOR BOARD:{}".format(board_string))
        for item in view_pocket:
            print(item)

    #print(replace_strings("8+",board))
    #print(replace_strings("5+",board))
    #print(replace_strings("cc+",board))
    #print(replace_strings("99+",board))
    # print_view(view)

def flop_generation():
    boards=[]
    all_flops = itertools.combinations(CARDS,3)
    for iterations in range(0,50):
         board_string = "".join(random.sample(CARDS,3))
         boards.append(board_string)
    #for flop in all_flops:
    #    boards.append("".join(flop))

    boards_min = [
        "KsTs5s",
        "7s7d6h",
        "Js9s9d",
        "Qs9s8d",
        "Td8s7s",
        "9s8d5h",
        "AsJd4h",
        "AdTs8s",
        "AsKd6s",
        "Ks8s3d",
        "QsJd7h",
        "Jd4s2s",
        "8d6s3h"
    ]

    boards_25pio = [
        "3s3dKs",
        "7s7d6s",
        "QsQd7s",
        "2d3sAs",
        "2s4d8c",
        "2s5dQc",
        "2s6dQc",
        "2d9sKs",
        "2sQsKd",
        "3s5d8c",
        "3sTdJc",
        "3sJsAd",
        "4s6sJd",
        "4s9dTc",
        "4sTsJd",
        "4dTsKs",
        "5s6dTc",
        "5s6dAc",
        "5d7s9s",
        "5s9sKd",
        "7d8sTs",
        "7d8sJs",
        "7sQsAs",
        "7sKsAd",
        "8s9dAc"
    ]

    boards_49pio =[
        "3s3d2c",
        "4s4d5s",
        "6s6dAs",
        "7s7d6s",
        "8s8dJs",
        "TsTdKs",
        "JsJd9s",
        "QsQdJc",
        "KsKd7s",
        "AsAd7s",
        "2s3d7c",
        "2d3s9s",
        "2s4dQc",
        "2s4dAc",
        "2s5dTc",
        "2s5sAd",
        "2d6s9s",
        "2s8dJs",
        "2dQsKs",
        "3s4s6s",
        "3s5s9d",
        "3d6sKs",
        "3s7dQc",
        "3d8s9s",
        "3s8sQs",
        "3s9dAc",
        "3dKsAs",
        "4s5dJc",
        "4s6dTc",
        "4s7s8d",
        "4s8dKc",
        "4sJsKd",
        "5s6d8c",
        "5s7s9s",
        "5s7dTc",
        "5dQsAs",
        "6s7dTc",
        "6s7dQc",
        "6dJsAs",
        "7s9dKc",
        "7sJdAs",
        "8s9dQc",
        "8sTsQs",
        "8sTdKc",
        "8sTdAs",
        "9sTdQc",
        "9dTsKs",
        "TsJdQc",
        "TsJsAd"
    ]

    boards_184pio=[
        "TsTdTc",
        "AsAdAc",
        "2s2d6c",
        "2s2dTc",
        "3s3d8s",
        "3s3dJc",
        "4s4d3c",
        "4s4dKc",
        "5s5d7c",
        "6s6d8s",
        "6s6d9s",
        "6s6d9c",
        "6s6dJs",
        "7s7dTs",
        "7s7dQc",
        "8s8d3s",
        "8s8dTc",
        "9s9d3s",
        "9s9d3c",
        "9s9dAc",
        "TsTd5c",
        "JsJd4c",
        "JsJd5c",
        "JsJd7c",
        "QsQd3c",
        "QsQd8s",
        "KsKd4s",
        "KsKd6c",
        "KsKd9c",
        "KsKdTc",
        "KsKdAs",
        "AsAd5c",
        "AsAdJs",
        "2s3s4s",
        "2s3d5c",
        "2s3d6c",
        "2s3d7c",
        "2s3d7s",
        "2s3s9d",
        "2s3dQc",
        "2s3dKs",
        "2d3sAs",
        "2s4d5c",
        "2s4s7d",
        "2d4s8s",
        "2s4d9c",
        "2d4sAs",
        "2s5d6s",
        "2d5s6s",
        "2s5dTc",
        "2s5dJs",
        "2d5sJs",
        "2s6s8d",
        "2s6dJc",
        "2s6sQd",
        "2s7d9s",
        "2s7dTc",
        "2d7sTs",
        "2s7dAs",
        "2s8dTc",
        "2s8sTs",
        "2d8sQs",
        "2s8dKc",
        "2d8sKs",
        "2s8dAc",
        "2sTdQc",
        "2dTsQs",
        "2dTsAs",
        "2sJdQs",
        "2sQsKd",
        "3d4s5s",
        "3s4s6s",
        "3s4dJc",
        "3s4dKs",
        "3s4dAc",
        "3d5s8s",
        "3s5sJd",
        "3s5dAc",
        "3s6s9d",
        "3s6dKc",
        "3d6sAs",
        "3s7d8c",
        "3s7d8s",
        "3s7sJs",
        "3s7dQc",
        "3s7dAc",
        "3s7sAd",
        "3s8d9c",
        "3d8sJs",
        "3s9dTc",
        "3s9sQs",
        "3sTsKd",
        "3sTdAc",
        "3dJsAs",
        "3dQsKs",
        "3sQsAs",
        "4d5sTs",
        "4s5dKc",
        "4s5sKd",
        "4s5dKs",
        "4d5sAs",
        "4s6d7s",
        "4d6s8s",
        "4s6d9c",
        "4s6sJs",
        "4s6dQc",
        "4s6dKc",
        "4s6dAc",
        "4s7d8c",
        "4s7sTd",
        "4d7sQs",
        "4d8s9s",
        "4s8dJc",
        "4s8dQc",
        "4d9sJs",
        "4s9sJs",
        "4s9dQc",
        "4sTdJc",
        "4sTsAd",
        "4sJdQc",
        "5d6s7s",
        "5s6d8s",
        "5d6s8s",
        "5s6dJc",
        "5s6sKs",
        "5s6dAc",
        "5d7s8s",
        "5s7d9s",
        "5d7s9s",
        "5s7sQd",
        "5s7sAs",
        "5s8d9c",
        "5s8sAs",
        "5s9sTd",
        "5s9sQd",
        "5s9dQs",
        "5s9dKc",
        "5sTdQc",
        "5sTsQd",
        "5sTdKs",
        "5sTdAc",
        "5dJsQs",
        "5sJsAd",
        "6s7dTc",
        "6s7sKd",
        "6s7dAc",
        "6s8d9c",
        "6s8dTs",
        "6s8dQs",
        "6s9dTs",
        "6s9sAs",
        "6sTdJc",
        "6dTsAs",
        "6sJdKs",
        "6sQsKs",
        "6sQdAc",
        "7s8sTd",
        "7s8dJc",
        "7s9dJc",
        "7s9sKs",
        "7sTdAc",
        "7sQsKd",
        "7dQsKs",
        "7sQsAd",
        "7sQdAs",
        "7dKsAs",
        "8s9dTs",
        "8s9sAd",
        "8sTdJs",
        "8sJdKc",
        "8sKsAd",
        "8dKsAs",
        "9dTsJs",
        "9sTsAd",
        "9sJdQc",
        "9sQsKd",
        "9sQsAd",
        "9sKdAs",
        "TdJsQs",
        "TsJsKs",
        "JsQdKc",
        "JdQsAs",
        "JsKsAd",
        "QsKdAs"
    ]

    cath={"TwoTone":0,
                 "Rainbow":0,
                 "Monotone":0,
                 "Straight":0,
                 "1 Straight":0,
                 "2 Straights":0,
                 "3 Straights":0,
                 "Trip":0,
                 "Paired":0,
                 "Unpaired":0,
                 "A":0,
                 "K":0,
                 "Q":0,
                 "J":0,
                 "T":0,
                 "9":0,
                 "8":0,
                 "7":0,
                 "6":0,
                 "5":0,
                 "4":0,
                 "3":0,
                 "2":0}
    #boards = boards_25pio
    #boards = boards_min
    for board in boards:
        print(board + ",")
    count_total=len(boards)
    for board in boards:
        board = board_util.parse_board(board)
        fd = board_util.return_flushdraws(board)
        if board_util.return_flushes(board):
            cath["Monotone"]+=1
        elif board_util.return_flushdraws(board)[0]:
            cath["TwoTone"]+=1
        else:
            cath["Rainbow"]+=1
        straights=board_util.return_straights(board)
        straights = list(itertools.chain.from_iterable(straights))
        if straights:
            cath["Straight"]+=1
            if len(straights) == 1:
                cath["1 Straight"]+=1
            elif len(straights)==2:
                cath["2 Straights"]+=1
            elif len(straights) == 3:
                cath["3 Straights"]+=1
        rank_count = board_util.return_rank_counts(board)
        if rank_count[2] != []:
            cath["Trip"]+=1
        elif rank_count[1] != []:
            cath["Paired"]+=1
        else:
            cath["Unpaired"]+=1
        rank_matched = False
        for rank in RANKS:
            if rank_matched:
                break
            for card in board:
                if rank in card:
                    cath[rank]+=1
                    rank_matched=True
                    break
    cath_percent = {k: round(v/count_total*100,2) for k, v in cath.items()}
    print(cath_percent)

if (__name__ == '__main__'):
    flop_generation()
    #try_it()
