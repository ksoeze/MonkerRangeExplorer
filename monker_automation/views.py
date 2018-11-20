#!/usr/bin/env python3

from monker_automation.utils import *
import monker_automation.board as board_util


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
    ranks = board_util.return_ranks(board)
    rank_count_list = board_util.return_rank_counts(board)
    if rank_count_list[0] != [] and RANK_ORDER[rank_count_list[0][0]] > RANK_ORDER[rank_count_list[3][0]]:
        view.append([rank_count_list[0][0]*2])
    view += regroup_list(board_util.return_pairs(board),
                         QUAD_BOARD_PAIR_GROUPING)
    kickers = board_util.return_kickers(board)
    view.append([kickers[0]+kickers[1], kickers[0] +
                 kickers[2], kickers[0]+kickers[3]])
    view.append([kickers[0]])
    return view


def trips_board(board):
    view = []
    rank_count_list = board_util.return_rank_counts(board)
    if board_util.return_str_flushes(board) != []:
        view.append(board_util.return_str_flushes(board))
    view.append(board_util.return_fulls_or_better(board))
    for card in rank_count_list[0]:
        if RANK_ORDER[card] > RANK_ORDER[rank_count_list[2][0]]:
            view.append([card*2])
    view += regroup_list(board_util.return_pairs(board),
                         QUAD_BOARD_PAIR_GROUPING)
    flushes = board_util.return_flushes(board)
    if flushes:
        flushes = [flushes[0][1:]]
        view.append(flushes)
        return view
    straights = board_util.return_straights(board)
    if straights:
        view.append(straights)
    return view


def paired_board(board):
    view = []
    ranks = board_util.return_ranks(board)
    suits = board_util.return_suits(board)
    rank_count_list = board_util.return_rank_counts(board)

    intersections = board_util.hand_board_intersections(board)
    pairs = board_util.return_pairs(board)
    kickers = board_util.return_kickers(board)

    fd = board_util.return_flushdraws(board)

    str_draws = board_util.return_straight_draws(board)

    if board_util.return_str_flushes(board) != []:
        view.append(board_util.return_str_flushes(board))
    view += regroup_list(board_util.return_fulls_or_better(board),
                         PAIRED_BOARD_FULL_OR_BETTER_GROUPING)

    flushes = board_util.return_flushes(board)
    straights = board_util.return_straights(board)

    if flushes:
        view.append([[flushes[0]], rank_count_list[1]])
        view.append([[flushes[0]], [rank for rank in rank_count_list[0]
                                    if RANK_ORDER[rank] > RANK_ORDER[rank_count_list[1][0]]]])
        view.append([[flushes[0][1:]], rank_count_list[1]])
        view += (regroup_list(flushes, FLUSH_GROUPING))
    elif straights:
        view.append([[straights[0]], rank_count_list[1]])
        view.append([[straights[0]], [rank for rank in rank_count_list[0]
                                      if RANK_ORDER[rank] > RANK_ORDER[rank_count_list[1][0]]]])
        if len(straights) > 1:
            view.append([[straights[1:]], rank_count_list[1]])
        view += (regroup_list(straights, STRAIGHT_GROUPING))

    if not flushes and not straights:

        view.append([kickers[0]+intersections[0]])
        view.append([kickers[1]+intersections[0],
                     kickers[1]+intersections[0]])

    view.append([intersections[0]])

    fd_1, fd_2 = board_util.return_flushdraws(board)
    straight_draws = board_util.return_straight_draws(board)
    overpairs = board_util.return_over_pairs(board)
    top_pair = rank_count_list[0][0]

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd = [fd_1[0]]
        fd = [fd_1[0][1:]]
        if fd_2:
            nfd.append(fd_2[0])
            fd.append(fd_2[0][1:])
        # nfd + best 2 overpairs and best pair intersection on board
        view.append([nfd, overpairs[:2]+[top_pair]])
        # any fd with sd value
        view.append([fd, overpairs[:2]+[top_pair]])
        # any fd with any straight draw
        if straight_draws:
            view.append([fd, straight_draws])
        # nfd no decent sd value
        view.append(nfd)
        # bare fd
        view.append(fd)

        # nfd blocker?
        view.append([a[:2] for a in nfd])
    if straight_draws:
        # better straight draws + op or tp
        view.append([overpairs[:2]+[top_pair],
                     straight_draws[:len(straight_draws)//2]])
        # better straight draws
        view.append(straight_draws[:len(straight_draws)//2])

        # weak straight draws + sd value
        view.append([overpairs[:2]+[top_pair],
                     straight_draws[len(straight_draws)//2:]])

        # weak straight draws
        view.append(straight_draws[len(straight_draws)//2:])

    if overpairs:
        view += regroup_list(overpairs, OVERPAIR_GROUPING)

    # top pair
    view.append([top_pair])

    # other 1 pair intersections
    if rank_count_list[0][1:]:
        view.append(rank_count_list[0][1:])

    return view


def flush_board(board):
    flushes = board_util.return_flushes(board)
    flush_blockers = board_util.return_flush_blockers(board)
    str_draws = board_util.return_straight_draws(board)
    overpairs = board_util.return_over_pairs(board)

    view = []

    view += regroup_list(flushes, FLUSH_GROUPING)

    made_hands = regroup_board_intersections(board)

    view += regroup_list(made_hands["sets"], SET_GROUPING)

    view += regroup_list(board_util.return_straights(board), STRAIGHT_GROUPING)
    view.append(made_hands["top2"])
    view.append(made_hands["topbottom"])
    view.append(made_hands["random2"])

    view.append(flush_blockers[0])
    view.append(flush_blockers[1])

    if str_draws:
        view.append([[flushes[0][1]], str_draws[0:len(str_draws)//2]])

    view.append([[flushes[0][1]], overpairs[0:2]+[made_hands["pair"][0]]])
    view.append(overpairs[0:2]+[made_hands["pair"][0]])

    view.append([flushes[0][1]])

    return view


def straight_board(board):
    view = []
    fd_1, fd_2 = board_util.return_flushdraws(board)
    straight_draws = board_util.return_straight_draws(board)
    straights = board_util.return_straights(board)
    grouped_strs = regroup_list(straights, STRAIGHT_GROUPING)

    made_hands = regroup_board_intersections(board)
    overpairs = board_util.return_over_pairs(board)
    blockerpairs = [straights[0][0]*2, straights[0][1]*2]
    overpairs = [pair for pair in overpairs if pair not in blockerpairs]

    if fd_1 and len(board_util.return_ranks(board)) != 5:
        nfd = [fd_1[0]]
        fd = [fd_1[0][1:]]
        if fd_2:
            nfd.append(fd_2[0])
            fd.append(fd_2[0][1:])

        # straights + fd or set
        for item in grouped_strs:
            view.append([item, fd + made_hands["sets"]])
        # sets + fd
        view.append([fd, made_hands["sets"]])
    else:
        # striaghts + set
        for item in grouped_strs:
            view.append([item, made_hands["sets"]])

    # straights bare
    view += grouped_strs
    # sets + 1 nutstraight card
    view.append([made_hands["sets"], [straights[0][0], straights[0][1]]])
    # sets
    view += regroup_list(made_hands["sets"], SET_GROUPING)
    if fd_1 and len(board_util.return_ranks(board)) != 5:
        # 2 pair + fd
        view.append([fd, made_hands["top2"] +
                     made_hands["topbottom"]+made_hands["random2"]])
        # nfd + str draw
        view.append([nfd, straight_draws[:len(straight_draws)//2]])
        # fd + str draw
        view.append([fd, straight_draws[:len(straight_draws)//2]])
        # fd + blockerpairs
        view.append([fd, blockerpairs])
        # nfd bare
        view.append(nfd)
        # fd bare
        view.append(fd)
    # top2 and topbottom + 1 blocker
    view.append([made_hands["top2"]+made_hands["topbottom"],
                 [straights[0][0], straights[0][1]]])
    view.append(made_hands["top2"])
    view.append(made_hands["topbottom"])
    view.append(made_hands["random2"])

    # nut straightblockers
    view.append(blockerpairs[:1])
    view.append(blockerpairs[1:])

    # overpairs + str draws
    view.append([overpairs, straight_draws[:len(straight_draws)//2]])
    # overpairs
    view += regroup_list(overpairs, OVERPAIR_GROUPING)
    # str draws
    view.append(straight_draws[:len(straight_draws)//2])
    # 1 str blocker
    view.append([straights[0][0], straights[0][1]])

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
        view.append([fd, made_hands["top2"]+made_hands["topbottom"]])

        # nfd + any 2, str_draws, tp, nut overpair
        view.append([nfd, made_hands["random2"] +
                     [made_hands["pair"][0]] + overpairs[:2]])
        # nfd + straight draws
        if straight_draws:
            view.append([nfd, straight_draws[:len(straight_draws)//2]])
        # nfd
        view.append(nfd)
        # fd + any 2, tp, straight draws
        view.append([fd, made_hands["random2"] +
                     [made_hands["pair"][0]] + straight_draws[:len(straight_draws)//2]])
        # fd + op
        view.append([fd, overpairs])
        # fd
        view.append(fd)
    # set, top 2 + str draws
    if straight_draws:
        view.append([made_hands["sets"]+made_hands["top2"],
                     straight_draws[:len(straight_draws)//2]])
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
        view.append([nfd_blocker, overpairs+made_hands["pair"][:1]])
        # nfd_blocker + str draw
        view.append([nfd_blocker, straight_draws[:len(straight_draws)//2]])
        # nfd_blocker bare
        view.append(nfd_blocker)
        # 2nfd blocker overall
        view.append(secnfd_blocker)

    if straight_draws:
        # op, tp + str draw
        view.append([overpairs+made_hands["pair"][:1],
                     straight_draws[:len(straight_draws)//2]])
        # str draw bare
        view.append(straight_draws[:len(straight_draws)//2])
    # op bare
    view += regroup_list(overpairs, OVERPAIR_GROUPING)
    # board pairs
    view += regroup_list(made_hands["pair"], PAIR_GROUPING)

    return view


def get_view(board, view_type):
    board = board_util.parse_board(board)
    rank_count_list = board_util.return_rank_counts(board)

    if rank_count_list[3] != []:
        return quad_board(board)
    if rank_count_list[2] != []:
        return trips_board(board)
    if rank_count_list[1] != []:
        return paired_board(board)
    if board_util.return_flushes(board):
        return flush_board(board)
    if board_util.return_straights(board):
        return straight_board(board)

    return std_board(board)


def view_item_to_str(item):
    if not item:
        return ""
    string = ""
    if type(item[0]) == str:
        for i in item:
            string += i+","
        string = string[:-1]+"\n"
    elif type(item[0]) == list and len(item) == 2:
        string1 = ""
        for i in item[0]:
            string1 += i+","
        string1 = "("+string1[:-1]+"):"
        string2 = ""
        for i in item[1]:
            string2 += i+","
        string2 = "("+string2[:-1]+")"
        string = string1 + string2+"\n"
    return string


def print_default_view(view):
    with open(DEFAULT_VIEW_NAME, "w") as f:
        f.write(TOP_VIEW_LINE)
        f.write("\n")
        for item in view:
            string = view_item_to_str(item)
            f.write(string)
            f.write(string)
            f.write("\n")


def test():
    board_string = "KdJh5h"
    view = get_view(board_string, VIEW_TYPES[0])
    print_default_view(view)


if (__name__ == '__main__'):
    test()
