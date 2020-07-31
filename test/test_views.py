import os
import pickle
import re
import pytest
from monker_automation.utils import *
from monker_automation.views import get_view, combine_views
from monker_automation.range import hand_in_range
from monker_automation.range_analysis import create_regex_from_view, read_data

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
