import pytest
from monker_automation.gui import read_situation_and_save_ranges
from monker_automation.views import get_view
from monker_automation.range import get_view_results
from monker_automation.plot import plot_default, plot_range_distribution
import pickle
from monker_automation.utils import *
import logging


@pytest.fixture()
def read_infos():
    with open("infos_pickle", "rb") as f:
        infos = pickle.load(f)
        yield infos


@pytest.fixture()
def read_results():
    with open("results_pickle", "rb") as f:
        total_results, action_results = pickle.load(f)
        yield total_results, action_results


def test_KdJh5h_vs_cbet(read_infos,read_results):
    new_infos = read_situation_and_save_ranges()
    assert read_infos["actions"] == new_infos["actions"]
    assert read_infos["board"] == new_infos["board"]
    assert read_infos["line"] == new_infos["line"]

    board = new_infos["board"]
    view = get_view(board, VIEW_TYPES[0])
    actions = new_infos["actions"]
    total_results, action_results = get_view_results(actions, view)

    assert read_results[0] == total_results
    assert read_results[1] == action_results

    plot_default(total_results,action_results,actions)
    plot_range_distribution(total_results,action_results,actions)

def test_print_combo_output():
    logger = logging.getLogger()
    logger.setLevel("DEBUG")
    new_infos = read_situation_and_save_ranges()

    board = new_infos["board"]
    view = get_view(board, VIEW_TYPES[0])
    actions = new_infos["actions"]
    total_results, action_results = get_view_results(actions, view)

    for item in total_results["r"]:
        print(item)