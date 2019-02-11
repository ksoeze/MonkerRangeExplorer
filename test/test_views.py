import os
import pickle
import pytest
from monker_automation.utils import *
from monker_automation.views import get_view

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


@pytest.mark.parametrize("board, viewtype, view", [
    ("KhJd5h", VIEW_TYPES[0], get_compare_view("KhJd5h", VIEW_TYPES[0])),
    ("KhJd5h", VIEW_TYPES[1], get_compare_view("KhJd5h", VIEW_TYPES[1])),
    ("KhJd5h", VIEW_TYPES[2], get_compare_view("KhJd5h", VIEW_TYPES[2])),
    ("KhJd5h", VIEW_TYPES[3], get_compare_view("KhJd5h", VIEW_TYPES[3]))
])
def test_view(board, viewtype, view):
    filename = board + "-" + viewtype + "-pickle"
    filename = VIEW_DATA_DIR+filename
    if not os.path.isfile(filename):
        generate_reference_views(board)
    new_view = get_view(board, viewtype)
    for reference, compare in zip(view, new_view):
        assert reference == compare
