#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def combine_view_with_percent(total_results, cum="True"):
    ticks = []
    if cum:
        for view, p_cum in zip(total_results["v_str"], total_results["r_cum"]):
            if len(view) > 30:  # TODO with variable // cut long description
                view = view[:27] + "..."
            number = "{0:.{1}f}".format(p_cum, 0)
            ticks.append(view + " | " + "{:<3}".format(number))
    else:
        for view, p in zip(total_results["v_str"], total_results["r"]):
            if len(view) > 30:  # TODO with variable // cut long description
                view = view[:27] + "..."
            number = "{0:.{1}f}".format(p, 1)
            ticks.append(view + " | " + "{:<3}".format(number))
    return ticks


def combine_action_with_percent(action_results):
    ticks = []
    ticks.append("Total | 100")
    for action in action_results:
        percent = action_results[action]["p"][0]  # total % of this action
        number = "{0:.{1}f}".format(percent, 0)
        ticks.append(action + " | " + "{:<3}".format(number))
    return ticks


def plot_default(titel, total_results, action_results, actions, cumulative=True):
    bars = []
    base_value = np.array([0.0]*len(total_results["v_str"][1:]))

    for index in range(len(actions)):
        if "CHECK" in actions[index] or "CALL" in actions[index]:
            color = "#8FBC8B"
        elif "FOLD" in actions[index]:
            color = "#6DA2C0"
        elif "RAISE" in actions[index] or "BET" in actions[index]:
            color = "#E9967A"
        else:
            color = "b"
        if index == 0:
            y_axes = np.arange(len(total_results["v_str"][1:]))
            bar = plt.barh(
                y_axes, action_results[actions[index]]["p"][1:], 0.6, color=color)
            bars.append(bar)
        else:
            base_value += np.array(action_results[actions[index-1]]["p"][1:])
            y_axes = np.arange(len(total_results["v_str"][1:]))
            bar = plt.barh(
                y_axes, action_results[actions[index]]["p"][1:], 0.6, left=base_value, color=color)
            bars.append(bar)

    # plt.ylabel('')
    plt.title(titel)
    yticks = combine_view_with_percent(total_results, cumulative)[1:]
    plt.yticks(np.arange(len(yticks)), yticks)
    plt.xticks(np.arange(0, 100, 10))
    legend_texts = list(
        reversed(combine_action_with_percent(action_results)[1:]))  # TODO BAD HACK!! depends on order of actions
    plt.legend(bars, legend_texts)
    # plt.legend(bars, actions)
    plt.axvline(x=25, color="k", linewidth=1, linestyle="--")
    plt.axvline(x=50, color="k",  linewidth=1, linestyle="--")
    plt.axvline(x=75, color="k",  linewidth=1, linestyle="--")
    plt.show()


def plot_range_distribution(titel, total_results, action_results, actions):
    y_ticks = combine_action_with_percent(action_results)
    x_ticks = total_results["v_str"][1:]  # exclude total
    table = []
    table.append(total_results["r"][1:])  # again exclude total stuff
    for action in action_results:
        table.append(action_results[action]["r"][1:])

    table = [*zip(*table)]  # transpose

    bars = []
    base_value = np.array([0.0]*len(y_ticks))

    colors = plt.cm.inferno(np.linspace(0, 1, len(x_ticks)))
    colors = plt.cm.viridis(np.linspace(0, 1, len(x_ticks)))

    colors = [(1, 0, 0), (1, 1, 0), (0, 0, 1)]
    n_bins = np.linspace(0, 1, len(x_ticks))
    n_bins = len(x_ticks)
    colors = LinearSegmentedColormap.from_list("test", colors)
    colors = colors(np.linspace(0, 1, len(x_ticks)))

    for index in range(len(x_ticks)):
        if index == 0:
            y_axes = np.arange(len(y_ticks))
            bar = plt.barh(y_axes, table[index], 0.6, color=colors[index])
            bars.append(bar)
        else:
            base_value += np.array(table[index-1])
            y_axes = np.arange(len(y_ticks))
            bar = plt.barh(
                y_axes, table[index], 0.6, left=base_value, color=colors[index])
            bars.append(bar)

    plt.title(titel)
    plt.yticks(np.arange(len(y_ticks)), y_ticks)
    plt.xticks(np.arange(0, 150, 10))
    plt.legend(bars, x_ticks, loc='lower right')
    plt.axvline(x=25, color="k", linewidth=1, linestyle="--")
    plt.axvline(x=50, color="k",  linewidth=1, linestyle="--")
    plt.axvline(x=75, color="k",  linewidth=1, linestyle="--")
    #plt.axvline(x=100, linestyle="--")

    plt.show()
