#!/usr/bin/env python3

from monker_automation.utils import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.font_manager import FontProperties
import os
import io
from PIL import Image


def combine_view_with_percent(total_results):
    ticks = []
    for view, p_cum, p in zip(total_results["v_str"], total_results["r_cum"], total_results["r"]):
        if len(view) > 30:  # TODO with variable // cut long description
            view = view[:27] + "..."
        cum = "{0:.{1}f}".format(p_cum, 0)
        if len(cum) == 1:
            cum = "  "+cum
        elif len(cum) == 2:
            cum = " "+cum
        rel = "{0:.{1}f}".format(p, 1)
        ticks.append(view + " {}".format(rel))
    return ticks


def combine_action_with_percent(action_results):
    ticks = []
    ticks.append("Total")
    for action in action_results:
        percent = action_results[action]["p"][0]  # total % of this action
        number = "{0:.{1}f}".format(percent, 0)
        ticks.append("{}% ".format(number) + action)
    return ticks


def plot_default(total_results, action_results, actions, cumulative=True):
    actions = list(reversed(actions))
    bars = []
    bars2 = []
    base_value = np.array([0.0]*len(total_results["v_str"][1:]))

    # figure basic settings
    plt.figure(figsize=(8.27, 6))
    plt.subplots_adjust(left=0.40, bottom=0.05, right=0.95, top=0.95)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    num_bets = 0
    for index in range(len(actions)):
        if "CHECK" in actions[index] or "CALL" in actions[index]:
            color = "#8FBC8B"
        elif "FOLD" in actions[index]:
            color = "#6DA2C0"
        elif "RAISE" in actions[index] or "BET" in actions[index]:
            if num_bets == 1:
                color = "#B15B4A"
            elif num_bets == 2:
                color = "#CF7D65"
            elif num_bets == 3:
                color = "#E9967A"
            elif num_bets == 0:
                color = "#873C2D"
            num_bets += 1
        else:
            color = "b"
        if index == 0:
            y_axes = np.arange(len(total_results["v_str"][1:]))
            bar = ax2.barh(
                y_axes, action_results[actions[index]]["p"][1:], 0.6, color=color)
            bar2 = ax1.barh(
                y_axes, action_results[actions[index]]["p"][1:], 0.6, color=color)
            bars.append(bar)
            bars2.append(bar2)
        else:
            base_value += np.array(action_results[actions[index-1]]["p"][1:])
            y_axes = np.arange(len(total_results["v_str"][1:]))
            bar = ax2.barh(
                y_axes, action_results[actions[index]]["p"][1:], 0.6, left=base_value, color=color)
            bar2 = ax1.barh(
                y_axes, action_results[actions[index]]["p"][1:], 0.6, left=base_value, color=color)
            bars.append(bar)
            bars2.append(bar2)

    # ax1.ylabel('')
    # ax1.title(titel)
    yticks = combine_view_with_percent(total_results)[1:]
    ax1.set_yticks(np.arange(len(yticks)))
    ax1.set_yticklabels(yticks)
    # for tick in ax1.get_yticklabels():
    #    tick.set_fontname("DejaVu Sans Mono")
    yticks = ["{0:.{1}f}".format(i, 0).format(i)
              for i in total_results["r_cum"][1:]]
    ax2.set_yticks(np.arange(len(yticks)))
    ax2.set_yticklabels(yticks)

    ax1.set_xticks(np.arange(0, 100, 10))
    # FIXMEEEE!! depends on order of actions!
    legend_texts = list(
        reversed(combine_action_with_percent(action_results)[1:]))
    #ax1.legend(bars, legend_texts)
    ax2.legend(bars, legend_texts,  loc='upper right')
    # ax1.legend(bars, actions)
    ax2.axvline(x=25, color="k", linewidth=1, linestyle="--")
    ax2.axvline(x=50, color="k",  linewidth=1, linestyle="--")
    ax2.axvline(x=75, color="k",  linewidth=1, linestyle="--")
    filename = os.path.join(DEFAULT_REPORT_DIRECTORY, STRATEGY_PNG_NAME)
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight', pad_inches=0)
    # plt.show()


def plot_range_distribution(total_results, action_results, actions):
    actions = list(reversed(actions))
    y_ticks = combine_action_with_percent(action_results)
    # exclude total
    x_ticks = [
        i[:27]+"..." if len(i) > 30 else i for i in total_results["v_str"][1:]]
    table = []
    table.append(total_results["r"][1:])  # again exclude total stuff
    for action in action_results:
        table.append(action_results[action]["r"][1:])

    table = [*zip(*table)]  # transpose

    bars = []
    base_value = np.array([0.0]*len(y_ticks))

    # figure basic settings
    plt.figure(figsize=(8.27, 4.65))
    plt.subplots_adjust(left=0.14, bottom=0.08, right=0.80, top=0.95)

    colors = plt.cm.inferno(np.linspace(0, 1, len(x_ticks)))
    colors = plt.cm.viridis(np.linspace(0, 1, len(x_ticks)))

    colors = [(0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0), (1, 1, 0)]
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

    # plt.title(titel)
    plt.yticks(np.arange(len(y_ticks)), y_ticks)
    plt.xticks(np.arange(0, 100, 10))
    plt.legend(bars, x_ticks, loc='upper left',
               fontsize="xx-small", bbox_to_anchor=(1.01, 1))
    plt.axvline(x=25, color="k", linewidth=1, linestyle="--")
    plt.axvline(x=50, color="k",  linewidth=1, linestyle="--")
    plt.axvline(x=75, color="k",  linewidth=1, linestyle="--")
    # plt.axvline(x=100, linestyle="--")
    filename = os.path.join(DEFAULT_REPORT_DIRECTORY, RANGE_PNG_NAME)
    plt.savefig(filename, dpi=200, bbox_inches='tight', pad_inches=0)
    # plt.show()
    # return plt
