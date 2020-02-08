#!/usr/bin/env python3

from monker_automation.utils import *
import monker_automation.board as board_util
import os
import logging


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
        view.append(board_util.return_str_flushes(board))

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


def clean(view):
    new_view = []
    for item in view:
        if len(item) == 0:  # discard empty view entry
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
    print("Unsupported VIEW TYPE")
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


def test():
    board_string = "7d8c6c5s4d"
    view_default = get_view(board_string, VIEW_TYPES[0])
    view_made = get_view(board_string, VIEW_TYPES[1])
    view_draws = get_view(board_string, VIEW_TYPES[2])
    view_blockers = get_view(board_string, VIEW_TYPES[3])

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

    # print_view(view)


if (__name__ == '__main__'):
    test()
