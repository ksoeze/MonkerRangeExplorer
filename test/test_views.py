import os
import pickle
import re
import pytest
import numpy as np
import pandas
from monker_automation.utils import *
from monker_automation.views import get_view, combine_views, view_item_to_str
from monker_automation.range import hand_in_range, get_view_results
from monker_automation.range_analysis import create_regex_from_view, read_data,heatmap
VIEW_DATA_DIR="./view_data/"

def generate_reference_views(board):
    for view_type in VIEW_TYPES:
        view = get_view(board, view_type)
        filename = board + "-" + view_type + "-pickle"
        filename = VIEW_DATA_DIR+filename
        print("GENERATING {} view for board: {}".format(view_type, board))
        for item in view:
            print(item)
        print("\n\n")
        with open(filename, "wb") as f:
            pickle.dump(view, f)


def get_compare_view(board, view_type):
    filename = board + "-" + view_type + "-pickle"
    filename = VIEW_DATA_DIR+filename
    with open(filename, "rb") as f:
        return pickle.load(f)


@pytest.mark.parametrize("board, viewtype", [
    ("KhJd5h", VIEW_TYPES[0]),
    ("KhJd5h", VIEW_TYPES[1]),
    ("KhJd5h", VIEW_TYPES[2]),
    ("KhJd5h", VIEW_TYPES[3]),
    ("4c4d4hTcQs", VIEW_TYPES[0]),
    ("4c4d4h2c3s", VIEW_TYPES[0]),
    ("8s7c2d6h",VIEW_TYPES[0]),
    ("6h6d2h2dTc",VIEW_TYPES[0]),
    ("6h6d6h2d2c",VIEW_TYPES[0]),
    ("QhQd6h2d2c",VIEW_TYPES[0]),
    ("AcJc3dQhKd", VIEW_TYPES[0]),
    ("Qc6h5cQd6d", VIEW_TYPES[0]),
    ("AcQd7sAd", VIEW_TYPES[0]),
    ("KdJc4s5cAh",VIEW_TYPES[0]),
])
def test_view(board, viewtype):
    filename = board + "-" + viewtype + "-pickle"
    filename = VIEW_DATA_DIR+filename
    if not os.path.isfile(filename):
        generate_reference_views(board)
    view=get_compare_view(board,viewtype)
    new_view = get_view(board, viewtype)
    for reference, compare in zip(view, new_view):
        assert reference == compare

@pytest.mark.parametrize("board, viewtype1, viewtype2", [
    ("KhJd5h",VIEW_TYPES[1],VIEW_TYPES[2])
])
def test_combine_view(board,viewtype1,viewtype2):
    views,megaview = combine_views(board,viewtype1,viewtype2)
    for view in views:
        print("Next View for board: {}".format(board))
        for item in view:
            print(item)
        print("\n\n")
    print("MEGA View for board: {}".format(board))
    for item in megaview:
        print(item)
    print("\n\n")


def test_new_matching_method():
    filename = os.path.join(
    DEFAULT_REPORT_DIRECTORY, PICKLE_INFOS)
    with open(filename, "rb") as f:
        hand_lists = pickle.load(f)
        total_results = pickle.load(f)
        action_results = pickle.load(f)
        actions = pickle.load(f)
        board = pickle.load(f)
    for view in VIEW_TYPES:
        view_list = get_view(board,view)
        for view_item in view_list:
            if type(view_item[0]) != str:
                pattern1 = create_regex_from_view(view_item[0])
                pattern2 = create_regex_from_view(view_item[1])
            else:
                pattern1 = create_regex_from_view(view_item)
                pattern2 = ".*"
            for hand in hand_lists[0][1]:
                old_match = hand_in_range(hand[0],view_item)
                new_match = bool(re.search(pattern1,hand[0])) and bool(re.search(pattern2,hand[0]))
                if old_match != new_match:
                    print("-------------------------------------------------------------------------")
                    print(hand)
                    print(view_item)
                    print(pattern1)
                    print(pattern2)
                    print(old_match)
                    print(new_match)
                    assert old_match == new_match

def convert_heatmap_to_results(heat_map, actions, column):
    heat_map_total = sum(heat_map.values())
    heat_map_total = heat_map_total[column]
    total_results = {}
    total_results["v_str"] = heat_map_total.index.tolist()
    total_results["r"] = heat_map_total.values.tolist()
    total_results["r"] = [x / total_results["r"][0] * 100 for x in total_results["r"]]
    total_results["r_cum"] = [total_results["r"][0]] + np.cumsum(total_results["r"][1:-1]).tolist()  # +[100]
    total_results["r_cum"] += [total_results["r_cum"][-1] + total_results["r"][-1]]
    action_results = {}
    for action in actions:
        results = {}
        action_percent = heat_map[action][column].div(heat_map_total) * 100
        results["p"] = action_percent.values.tolist()
        action_weight = heat_map[action][column].div(heat_map[action]["total"]["total"]) * 100
        results["r"] = action_weight.values.tolist()
        results["r_cum"] = [results["r"][0]] + np.cumsum(results["r"][1:-1]).tolist()  # +[100]
        results["r_cum"] += [results["r_cum"][-1] + results["r"][-1]]
        action_results[action] = results
    return total_results, action_results

def compare_action_results(old,new,old_index_inc=0):
    for action in list(old.keys()):
        for value in list(old[action].keys()):
            if value == "r_cum": # not correct for combined view
                continue
            old_data=old[action][value]
            new_data=new[action][value]
            for i in range(1,len(new_data)):
                if abs(old_data[i+old_index_inc] - new_data[i]) > 0.0001 and not pandas.isna(new_data[i]):
                    diff = old_data[i+old_index_inc]/new_data[i]
                    if not(0.999 < diff < 1.001):
                        print("OLD Data")
                        print(old)
                        print("NEW Data")
                        print(new)
                    assert(0.999 < diff < 1.001)

def test_compare_report_generation():
    filename = os.path.join(
    DEFAULT_REPORT_DIRECTORY, PICKLE_INFOS)
    with open(filename, "rb") as f:
        hand_lists = pickle.load(f)
        total_results = pickle.load(f)
        action_results = pickle.load(f)
        actions = pickle.load(f)
        board = pickle.load(f)

    new_data, _ , _ = read_data(actions, board, "MADE_HANDS")

    row_view = "MADE_HANDS"
    column_view = "FLUSH_SUITS"
    old_views, old_megaview = combine_views(board, column_view, row_view, ignore_first_entry=False)
    old_views[0] = [[["sss"],["hhh"]]] + old_views[0]
    row_view = get_view(board,row_view)
    column_view = get_view(board,column_view)

    test_view_types= ["MADE_HANDS", "DRAWS", "BLOCKERS", "DRAWS_BLOCKERS","FLUSH_SUITS","STR_DRAWS","PAIRS", "BOARD_RANK_INTERACTION"]

    # default row view

    for view in test_view_types:
        view = get_view(board,view)
        heat = heatmap(actions,new_data,view,column_view, True, True)
        new_total_results, new_action_results = convert_heatmap_to_results(heat,actions,"total")
        old_total_results, old_action_results = get_view_results(actions, view)
        compare_action_results(old_action_results,new_action_results)

    # default row view exclude

    for view in test_view_types:
        view = get_view(board,view)
        heat = heatmap(actions,new_data,view,column_view, False, True)
        new_total_results, new_action_results = convert_heatmap_to_results(heat,actions,"total")
        old_total_results, old_action_results = get_view_results(actions, view,exclude=False)
        compare_action_results(old_action_results,new_action_results)

    # heat = heatmap(actions,new_data,row_view,column_view, True, True)
    #
    # for index in range(len(column_view)):
    #     old_total_results, old_action_results = get_view_results(actions, old_views[index])
    #     new_total_results, new_action_results = convert_heatmap_to_results(heat,actions,view_item_to_str(column_view[index]))
    #     compare_action_results(old_action_results,new_action_results,old_index_inc=1)

    # very slow -- takes about 20min

    for row_view_name in test_view_types:
        for column_view_name in test_view_types:
            old_views, old_megaview = combine_views(board, column_view_name, row_view_name, ignore_first_entry=False)
            old_views[0] = [[["sss"],["hhh"]]] + old_views[0]
            row_view = get_view(board,row_view_name)
            column_view = get_view(board,column_view_name)
            heat = heatmap(actions,new_data,row_view,column_view, True, True)
            for index in range(len(column_view)):
                old_total_results, old_action_results = get_view_results(actions, old_views[index])
                new_total_results, new_action_results = convert_heatmap_to_results(heat,actions,view_item_to_str(column_view[index]))
                compare_action_results(old_action_results,new_action_results,old_index_inc=1)
            print("Finished test with row_view: {} and column_view: {}".format(row_view_name,column_view_name))