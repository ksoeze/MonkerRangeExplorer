#!/usr/bin/env python3
import pickle
import re

from monker_automation.utils import *
import os
import logging
import itertools
import pandas as pd
import seaborn as sns
import numpy as np

import matplotlib

matplotlib.use('svg')

import matplotlib.pyplot as plt
from monker_automation.views import get_view, expand_range
from monker_automation.range import view_item_to_str
from monker_automation.plot import plot_default, plot_range_distribution
from timebudget import timebudget

def create_regex_from_item(item):
    if len(item) == 1:
        pattern = item
    elif len(item) == 2:
        if item[0] in RANKS and item[1] in SUITS:  # flushblocker
            pattern = item
        else:
            pattern = item[0] + ".+" + item[1]
    elif len(item) == 3:
        if item[0] in RANKS and item[1] in SUITS and item[2] in SUITS:
            # specific flush (2nd entry is for cases with "AsKsXdXd in Kss)
            pattern = "(" + item[0] + item[1] + ".+" + item[2] + ")|(" + item[2] + ".*" + item[0] + item[1] + ")"
        elif item[0] in RANKS and item[1] in RANKS and item[2] in RANKS:  # oesd/wrap stuff
            pattern = item[0] + ".+" + item[1] + ".+" + item[2]
        elif item[0] in SUITS and item[1] in SUITS and item[2] in SUITS:  # 3flush combo
            pattern = item[0] + ".+" + item[1] + ".+" + item[2]
    elif len(item) == 4:  # wrap or str flush
        if item[0] in RANKS and item[1] in RANKS and item[2] in RANKS and item[3] in RANKS:
            pattern = item[0] + ".+" + item[1] + ".+" + item[2] + ".+" + item[3]
        elif item[0] in RANKS and item[1] in SUITS and item[2] in RANKS and item[3] in SUITS:
            pattern = item[0] + item[1] + ".*" + item[2] + item[3]
        elif item[0] == "A" and item[1] in SUITS and item[2] in SUITS and item[3] in SUITS: # for preflop only A high tripple suited
            pattern = item[0] + item[1] + ".+" + item[2] + ".+" + item[3]
        elif item[0] in SUITS and item[1] in SUITS and item[2] in SUITS and item[3] in SUITS:
            if item[0] == item[2]: # quad flush for now only
                pattern = item[0] + ".+" + item[1] + ".+" + item[2] + ".+" + item[3]
            elif item[0] != item[2]: # double suited only xxyy syntax
                pattern = "(?=.+" + item[0] + ".+" + item[1] + ")(.+" +item[2] + ".+" + item[3] + ")"
    elif len(item) == 5: # for preflop only Ahhdd
        if item[0] == "A" and item[1] in SUITS and item[2] in SUITS and item[3] in SUITS and item[4] in SUITS:
          pattern = "(?=.*" + item[0] + item[1] + ".+" + item[2] + ")(.+" +item[3] + ".+" + item[4] + ")"
    return "(" + pattern + ")"


def create_regex_from_view(view_list):
    if type(view_list[0]) != str:
        print("Only simple views supported for now")
        return re.compile("XXXX")
    pattern = "|".join([create_regex_from_item(x) for x in view_list])
    return pattern
    return re.compile(pattern)


def get_conditional_sum(data, action, prefix_row, prefix_column, item_row, item_column):
    if item_row == "total" and item_column == "total":
        sum = data[action + " Weight"].sum()
    elif item_row == "total":
        sum = data.loc[data[prefix_column + item_column] == True, action + " Weight"].sum()  # TODO eval / debug
    elif item_column == "total":
        sum = data.loc[data[prefix_row + item_row] == True, action + " Weight"].sum()
    else:
        sum = data.loc[(data[prefix_row + item_row] == True) & (
                    data[prefix_column + item_column] == True), action + " Weight"].sum()
    return sum

def action_heatmap(temp_data, action, row_index, column_index, heat_map):
    heat_map[action] = pd.DataFrame(index=row_index, columns=column_index)
    for row in row_index:
        for col in column_index:
            heat_map[action][col][row] = get_conditional_sum(temp_data, action, "ROW", "COLUMN", row, col)

#@timebudget
def heatmap(actions, data, row_list, column_list, exclude_row=True, exclude_column=True, invert_row=False, invert_column=False):
    # create axes and fill data list with view infos
    row_index = ["total"] + [view_item_to_str(x) for x in row_list] + ["other"]
    temp_data = add_view_info(data, row_list, "ROW", exclude_row,invert_row)
    # else:
    #     row_index = ["total"] + [view_item_to_str(x) for x in row_list]
    #     temp_data = add_view_info(data, row_list, "ROW", False)
    column_index = ["total"] + [view_item_to_str(x) for x in column_list] + ["other"]
    temp_data = add_view_info(temp_data, column_list, "COLUMN", exclude_column,invert_column)
    # else:
    #     column_index = ["total"] + [view_item_to_str(x) for x in column_list]
    #     temp_data = add_view_info(temp_data, column_list, "COLUMN", False)
    # one heatmap for every action

    heat_map = {}
    for action in actions:
        heat_map[action] = pd.DataFrame(index=row_index, columns=column_index)
        for row in row_index:
            for col in column_index:
                heat_map[action][col][row] = get_conditional_sum(temp_data, action, "ROW", "COLUMN", row, col)
    #
    # result_manager = Manager()
    # heat_map = result_manager.dict()
    # with Pool(len(actions)) as p:
    #     p.starmap(action_heatmap, [(temp_data,action, row_index, column_index, heat_map) for action in actions])
    return heat_map


def cut_lable(label):
    if len(label._text) > MAX_LABEL_LENGTH:
        label._text = label._text[:MAX_LABEL_LENGTH] + "..."
    return label


def plot_action(axs, heat_map, action, title="", subplot_row=0):
    heat_map_total = sum(heat_map.values())
    if "CHECK" in action or "CALL" in action:
        color = "#8FBC8B"
        color = "Greens"
    elif "FOLD" in action:
        color = "#6DA2C0"
        color = "Blues"
    elif "RAISE" in action or "BET" in action:
        color = "Reds"

    heat_map_draw = (heat_map[action].div(heat_map_total)) * 100

    g = sns.heatmap(heat_map_draw.iloc[::-1].fillna(value=np.nan), annot=True,
                    yticklabels=1, linewidths=1, cmap=color,
                    ax=axs[subplot_row][0], vmin=0, vmax=100, fmt=".0f")
    axs[subplot_row][0].title.set_text(action + " frequencies " + title)
    g.set_yticklabels([cut_lable(x) for x in g.get_yticklabels()], rotation=0)
    g.set_xticklabels([cut_lable(x) for x in g.get_xticklabels()], rotation=80)

    # print weights
    heat_map_draw = heat_map[action].div(heat_map[action]["total"]["total"]) * 100

    g = sns.heatmap(heat_map_draw.iloc[::-1].fillna(value=np.nan), annot=True,
                    yticklabels=1, linewidths=1, cmap=color,
                    ax=axs[subplot_row][1], vmin=0, vmax=100, fmt=".1f")
    axs[subplot_row][1].title.set_text(action + " range distribution in % " + title)
    g.set_yticklabels([cut_lable(x) for x in g.get_yticklabels()], rotation=0)
    g.set_xticklabels([cut_lable(x) for x in g.get_xticklabels()], rotation=80)



#@timebudget
def plot(heat_map, actions, subtitle_infos):
    fig, axs = plt.subplots(nrows=len(actions), ncols=2, figsize=(21, 21))
    fig.subplots_adjust(top=0.98, bottom=0.05, left=0.15, right=1, hspace=0.4,
                        wspace=0.3)
    row = 0
    for action in actions:
        plot_action(axs, heat_map, action, subtitle_infos[action], row)
        row += 1
    return fig, axs


#@timebudget
def plot_bar(heat_map, actions):
    # hack data and print it with old method from plot.py
    heat_map_total = sum(heat_map.values())
    heat_map_total = heat_map_total["total"]
    total_results = {}
    total_results["v_str"] = heat_map_total.index.tolist()
    total_results["r"] = heat_map_total.values.tolist()
    total_results["r"] = [x / total_results["r"][0] * 100 if total_results["r"][0] else 0 for x in total_results["r"]]
    total_results["r_cum"] = [total_results["r"][0]] + np.cumsum(total_results["r"][1:-1]).tolist()  # +[100]
    total_results["r_cum"] += [total_results["r_cum"][-1] + total_results["r"][-1]]
    action_results = {}
    for action in actions:
        results = {}
        action_percent = heat_map[action]["total"].div(heat_map_total) * 100
        results["p"] = action_percent.values.tolist()
        action_weight = heat_map[action]["total"].div(heat_map[action]["total"]["total"]) * 100
        results["r"] = action_weight.values.tolist()
        results["r_cum"] = [results["r"][0]] + np.cumsum(results["r"][1:-1]).tolist()  # +[100]
        results["r_cum"] += [results["r_cum"][-1] + results["r"][-1]]
        action_results[action] = results
    plot_default(total_results, action_results, actions, False)
    plot_range_distribution(total_results, action_results, actions, False)

#@timebudget
def add_view_info(data, view_list, prefix, exclude=True,invert=False):
    data[prefix] = False
    for view in view_list:
        pattern = create_regex_from_view(view)
        data[prefix + view_item_to_str(view)] = data["Hand"].apply(lambda row: bool(re.search(pattern, row)))
        #data[prefix + view_item_to_str(view)] = data["Hand"].str.contains(pat=pattern)
        # remove true values from this column if it has been matched before...probably possible in one step above?
        if exclude:
            if invert:
                data[prefix + view_item_to_str(view)] = data[prefix + view_item_to_str(view)] | data[prefix]
            else:
                data[prefix + view_item_to_str(view)] = data[prefix + view_item_to_str(view)] & ~data[prefix]
        # propagate new matches to total match column
        data[prefix] = data[prefix] | data[prefix + view_item_to_str(view)]
        # invert TODO debug
        if invert:
            data[prefix + view_item_to_str(view)] = ~data[prefix + view_item_to_str(view)]
    if invert:
        data[prefix + "other"] = data[prefix]
    else:
        data[prefix + "other"] = ~data[prefix]  # other hands are all hands not matched so far
    return data

    # else:
    #     for view in view_list:
    #         pattern = create_regex_from_view(view)
    #         data[prefix + view_item_to_str(view)] = data["Hand"].apply(lambda row: bool(re.search(pattern, row)))
    # return data


def get_view_list(view_type, board):
    if view_type in VIEW_TYPES:
        return get_view(board, view_type)
    if view_type == "RANKS":
        return [[x] for x in RANKS]
    if view_type == "SUITS":
        return [[x] for x in SUITS]
    if view_type == "PREFLOP_PAIRS_HIGH_CARD":
        view = [[x+x] for x in RANKS]
        view.append(["AK","AQ","AJ"])
        view.append(["A"])
        view.append(["KQ","KJ"])
        view.append(["K"])
        view.append(["Q"])
        view.append(["J","T"])
        return view
    if view_type == "PREFLOP_SUITS":
        view=[]
        view.append(["Ahhcc","Ahhdd","Ahhss","Acchh","Accdd","Accss","Addhh","Addss","Addcc","Asshh","Asscc","Assdd"])
        view.append(["hhcc","hhdd","hhss","ccdd","ccss","ddss"])
        view.append(["hhhh","dddd","cccc","ssss"])
        view.append(["Ahhh","Addd","Accc","Asss"])
        view.append(["hhh","ddd","ccc","sss"])
        view.append(["Ahh","Add","Acc","Ass"])
        view.append(["hh","dd","cc","ss"])
        return view
    if view_type == "PREFLOP_HIGH_CARD":
        view=[]
        view.append(["AKQ","AKJ","AKT","AQJ","AQT","AJT"])
        view.append(["AK","AQ","AJ","AT"])
        view.append(["A"])
        view.append(["KQ","KJ","KT"])
        view.append(["K"])
        view.append(["QJ","QT"])
        view.append(["Q"])
        view.append(["JT"])
        view.append(["J"])
        view.append(["T9"])
        view.append(["T"])
        return view
    logging.error("View Type not supported ({})".format(view_type))
    return []


def read_data(actions, board, filter_view):
    action_combinations = itertools.combinations(actions, 2)
    action_combinations = list(action_combinations)
    hand_infos = pd.DataFrame()
    for action in actions:
        file_name = os.path.join(RANGE_FOLDER, action + ".csv")
        action_info = pd.read_csv(file_name)
        action_info.columns = ['Hand', action + ' Weight', action + ' EV']
        values={action + ' Weight': 0}
        action_info.fillna(value=values,inplace=True)
        if hand_infos.empty:
            hand_infos = action_info
        else:
            hand_infos = hand_infos.merge(action_info)
    # clean up low weight
    hand_infos['Total Weight'] = sum([hand_infos[x + " Weight"] for x in actions])
    hand_infos.drop(hand_infos[hand_infos['Total Weight'] < MIN_WEIGHT].index, inplace=True)
    for combination in action_combinations:
        hand_infos[combination[0] + " vs " + combination[1]] = hand_infos[combination[0] + " EV"] - hand_infos[
            combination[1] + " EV"]
    view = get_view_list(filter_view, board)
    hand_infos = add_view_info(hand_infos, view, "", True)
    action_combinations = [x[0] + " vs " + x[1] for x in action_combinations]
    view = [view_item_to_str(x) for x in view]
    return hand_infos, view, action_combinations


#@timebudget
def get_ev_filtered_data(data, actions, filter_by_ev, ev_condition):
    if pd.isnull(data.loc[data.index[0], filter_by_ev]):
        logging.warning("Ranges dont contain EV informations...SKIP FILTER!")
        return actions, data

    # EV regret
    data['Total EV'] = sum([data[x + " EV"]*data[x + " Weight"] for x in actions])
    total_weight = data["Total Weight"].sum()
    total_ev = data["Total EV"].sum()/total_weight
    print("-"*50)
    print("Overall EV: {:.0f}".format(total_ev))
    for action in actions:
        total_action_ev = (data["Total Weight"]*data[action+" EV"]).sum()/total_weight
        regret = (total_ev - total_action_ev)/abs(total_ev)
        print("EV taking only Action {}: {:.0f} (Regret = {:.2f}%)".format(action,total_action_ev,regret*100))
    print("-"*50)

    filtered_actions = filter_by_ev.split(" vs ")
    data = data.drop(data[(data[filtered_actions[0] + ' Weight'] < MIN_QUIZ_WEIGHT) & (
                data[filtered_actions[1] + ' Weight'] < MIN_QUIZ_WEIGHT)].index)
     # EV regret only regarding filtered actions
    total_weight = data["Total Weight"].sum()
    total_ev = data["Total EV"].sum()/total_weight
    print("Overall EV for only {}: {:.0f}".format(filter_by_ev,total_ev))
    for action in filtered_actions:
        total_action_ev = (data["Total Weight"]*data[action+" EV"]).sum()/total_weight
        regret = (total_ev - total_action_ev)/abs(total_ev)
        print("EV taking only Action {}: {:.0f} (Regret = {:.2f}%)".format(action,total_action_ev,regret*100))
    print("-"*50)
    data = data.sort_values(by=filter_by_ev, ascending=False)
    while len(data) < ev_condition * 2:
        logging.info("Too little hands in range...cut by half")
        ev_condition = ev_condition // 2
    if data.loc[data.index[ev_condition], filter_by_ev] < 0:
        logging.info("Restrict EV condition to less hands since there are too little hands with EV {} > {}".format(filtered_actions[0], filtered_actions[1]))
    if data.loc[data.index[-ev_condition], filter_by_ev] > 0:
        logging.info("Restrict EV condition to less hands since there are too little hands with EV {} < {}".format(filtered_actions[0], filtered_actions[1]))
        #logging.info("Restrict EV condition to less hands {}".format(data.loc[data.index[ev_condition], filter_by_ev]))
    new_data = data.tail(ev_condition)
    new_data = new_data.append(data.head(ev_condition))
    return filtered_actions, new_data


def create_filter_view(range, board):
    range_list = []
    if not range:
        return range_list
    range = range.replace(" ", "")
    range = range.split(",")
    range = [expand_range(x, board) for x in range]
    range_items = []
    for item in range:
        range_items.append(item.split(","))
    range_items = [j for i in range_items for j in i]
    for item in range_items:
        item = expand_range(item, board)
        checked_item = ""
        if len(item) == 1 and (item[0] in RANKS or item[0] in SUITS):
            checked_item = item
        elif len(item) == 2:
            if item[0] in RANKS and item[1] in SUITS:  # flushblocker
                checked_item = item
            elif item[0] in SUITS and item[1] == item[0]:  # flush
                checked_item = item
            elif item[0] in RANKS and item[1] in RANKS:  # 2 ranks
                checked_item = "".join(sorted(item, key=lambda x: RANK_ORDER[x], reverse=True))
        elif len(item) == 3:
            if item[0] in RANKS and item[1] in SUITS and item[2] == item[1]:  # specific flush
                checked_item = item
            elif item[0] in RANKS and item[1] in RANKS and item[2] in RANKS:  # oesd/wrap stuff
                checked_item = "".join(sorted(item, key=lambda x: RANK_ORDER[x], reverse=True))
            elif item[0] in SUITS and item[1]  == item[0] and item[2] in item[0]:  # 3 of 1 suit
                checked_item = item
        elif len(item) == 4:  # wrap or str flush
            if item[0] in RANKS and item[1] in RANKS and item[2] in RANKS and item[3] in RANKS:
                checked_item = "".join(sorted(item, key=lambda x: RANK_ORDER[x], reverse=True))
            elif item[0] in RANKS and item[1] in SUITS and item[2] in RANKS and item[3] in SUITS:
                if RANK_ORDER[item[0]] >= RANK_ORDER[item[2]]:
                    checked_item = item
                elif RANK_ORDER[item[0]] < RANK_ORDER[item[2]]:
                    checked_item = item[2:4] + item[0:2]
            elif item[0] == "A" and item[1] in SUITS and item[2] == item[1] and item[3] == item[1]: # for preflop only A high tripple suited
                checked_item = item
            elif item[0] in SUITS and item[1] in SUITS and item[2] in SUITS and item[3] in SUITS: #only double suited and quad suited for now
                if item[0] == item[1] and item[2] == item[3]:
                    checked_item = item
                elif item[0] == item[1] == item[2] == item[3]:
                    checked_item = item
        elif len(item) == 5: # for preflop only Axxyy
            if item[0] == "A" and item[1] in SUITS and item[1] == item[2] and item[3] in SUITS and item[3] == item[4] and item[1] != item[3]:
                checked_item = item
        if checked_item:
            range_list.append(checked_item)
        else:
            logging.warning("Invalid Filter Item: {}".format(item))
    return range_list


#@timebudget
def filter_hands(data, actions, board, hand_filter, hand_filter_exclude, filter_item, filter_by_ev, ev_condition):
    hand_filter_view = create_filter_view(hand_filter, board)
    hand_filter_exclude_view = create_filter_view(hand_filter_exclude, board)

    combo_count = {}

    combo_count["total"] = data["Total Weight"].sum()
    combo_count["filter"] = combo_count["total"]
    if hand_filter_view != []:
        data = add_view_info(data, [hand_filter_view], "HAND FILTER", exclude=False)
        data = data.drop(data[data["HAND FILTER" + view_item_to_str(hand_filter_view)] != True].index)
        combo_count["filter"] = data["Total Weight"].sum()

    combo_count["filter excl"] = combo_count["filter"]
    if hand_filter_exclude_view != []:
        data = add_view_info(data, [hand_filter_exclude_view], "HAND FILTER EXCLUDE", exclude=False)
        data = data.drop(data[data["HAND FILTER EXCLUDE" + view_item_to_str(hand_filter_exclude_view)] == True].index)
        combo_count["filter excl"] = data["Total Weight"].sum()

    combo_count["made hand"] = combo_count["filter excl"]
    if filter_item != "" and filter_item != "any":
        data = data.drop(data[data[filter_item] != True].index)
        combo_count["made hand"] = data["Total Weight"].sum()

    combo_count["final"] = combo_count["made hand"]
    if filter_by_ev != "NO":
        actions, data = get_ev_filtered_data(data, actions, filter_by_ev, ev_condition)
        combo_count["final"] = data["Total Weight"].sum()

    combo_count["hand_filter_str"] = view_item_to_str(hand_filter_view)
    combo_count["hand_filter_excl_str"] = view_item_to_str(hand_filter_exclude_view)
    combo_count["hand_item_str"] = filter_item

    return actions, data, combo_count

#@timebudget
def update_plot(data, actions, board, hand_filter, hand_filter_exclude, filter_item, filter_by_ev, ev_condition,
                row_view, column_view, row_exclude=True, column_exclude=True,row_invert=False, column_invert=False):
    # TODO get total weights and relative weights and show info somehow
    # TODO implement filter
    # TODO implement filter by ev -- DONE but hand condition often not suitable
    # TODO handle subtitle infos
    actions, data, combo_counts = filter_hands(data, actions, board, hand_filter, hand_filter_exclude, filter_item,
                                               filter_by_ev, ev_condition)

    sns.set()
    heat = heatmap(actions, data, row_view, column_view, row_exclude, column_exclude,row_invert,column_invert)

    # Print total weights just for infos
    print("Total Weights:")
    heat_map_total = sum(heat.values())
    heat_map_total_weight = heat_map_total.div(heat_map_total["total"]["total"])*100
    heat_map_total_weight=heat_map_total_weight.iloc[::-1]

    if PRINT_TOTAL_WEIGHTS:
        heat_map_total_weight_ = heat_map_total_weight.copy()
        heat_map_total_weight_.columns = [x[:15]+"..." if len(x)>18 else x for x in heat_map_total_weight.columns]
        with pd.option_context('display.max_rows', None,
                               'display.max_columns', None,
                               'display.float_format', '{:,.1f}'.format,
                               'display.width', None,
                               'display.max_colwidth', 18):
            print(heat_map_total_weight_)

    subtitle_infos = {}
    for action in actions:
        subtitle_infos[action] = " (total combos: {:.0f} ({:.0f}%))".format(heat[action]["total"]["total"],
                                                                            heat[action]["total"]["total"] /
                                                                            combo_counts["final"] * 100
                                                                            if combo_counts["final"] else 0)

    fig, axs = plot(heat, actions, subtitle_infos)
    plot_bar(heat, actions)
    return fig, combo_counts


def quiz_freq(hand, actions):
    action_list = []
    main_action = (0, 0)
    for i in range(len(actions)):
        action_list.append([hand.iloc[0][actions[i] + " Weight"], hand.iloc[0][actions[i] + " EV"]])
        if hand.iloc[0][actions[i] + " Weight"] > main_action[0]:
            main_action = (hand.iloc[0][actions[i] + " Weight"], i)
    return main_action, action_list


def quiz_get_main_ev(hand_info):
    ev = 0
    ev_diff = 0
    for i in range(len(hand_info["actions"])):
        action_ev = hand_info["actions"][i][1]
        if action_ev == -float('inf'):
            return ev, ev_diff
        ev += action_ev * hand_info["actions"][i][0] / hand_info["total_weight"]
        if i != hand_info["main_action"][1]:
            action_ev_diff = hand_info["actions"][hand_info["main_action"][1]][1] - action_ev
            if action_ev_diff > 0:
                if ev_diff == 0:
                    ev_diff = action_ev_diff
                else:
                    if action_ev_diff < ev_diff:
                        ev_diff = action_ev_diff
    return ev, ev_diff


def quiz_valid_ev(hand_info):
    if hand_info["actions"][0][1] == -float("inf"):
        return True
    if MIN_EV_DIFF * 1000 <= hand_info["ev_diff"] < MAX_EV_DIFF * 1000:
        return True
    else:
        return False


def get_quiz_hand(data, actions, board, hand_filter, hand_filter_exclude, filter_item, filter_by_ev, ev_condition):
    data = data.drop(data[data['Total Weight'] < MIN_QUIZ_WEIGHT].index)
    _, data, infos = filter_hands(data, actions, board, hand_filter, hand_filter_exclude, filter_item, filter_by_ev,
                                  ev_condition)
    if data.shape[0] < 5:
        logging.warning("Hand Filter too narrow (<5) combos")
        return None, infos
    counter = 0
    while True:
        hand = data.sample()
        hand_info = {
            "hand": hand.iloc[0]["Hand"],
            "total_weight": hand.iloc[0]["Total Weight"],
            "total_ev": 0,
            "ev_diff": 0,
            "actions": [],
            "main_action": (0, 0)
        }
        # ev_infos_colmns = [col for col in hand.columns if 'EV' in col]
        # hand_info["total_ev"]=hand[ev_infos_colmns].max(axis=1).iloc[0]
        if hand_info["total_weight"] < MIN_QUIZ_WEIGHT:
            continue
        hand_info["main_action"], hand_info["actions"] = quiz_freq(hand, actions)
        if hand_info["main_action"][0] / hand_info["total_weight"] < MIN_ACTION_FREQ:
            continue
        hand_info["total_ev"], hand_info["ev_diff"] = quiz_get_main_ev(hand_info)
        if quiz_valid_ev(hand_info):
            return hand_info, infos
        counter += 1
        if counter > 1000:
            break
    logging.warning("Couldnt find quiz hand matching filter criterias...")
    return None, infos


def print_ev_differences(self):
    action_combinations = itertools.combinations([i for i in range(len(self.actions))], 2)
    action_combinations = list(action_combinations)
    delim = ";"
    header_line = "Hand" + delim
    for action in self.actions:
        header_line += action + delim
        header_line += "EV " + action + delim
    for combo in action_combinations:
        header_line += "EV diff " + self.actions[combo[0]] + " " + self.actions[combo[1]] + delim
    hand_list = []
    for hand in self.overall_data:
        hand_line = hand["hand"] + delim
        for action in hand["actions"]:
            hand_line += "{0:.0f}%".format(action[0] / hand["total_weight"] * 100) + delim
            hand_line += "{0:.2f}".format(action[1] / 1000) + delim
        for combo in action_combinations:
            hand_line += "{0:.3f}".format((hand["actions"][combo[0]][1] - hand["actions"][combo[1]][1]) / 1000) + delim
        hand_list.append(hand_line)
    filename = os.path.join(
        DEFAULT_REPORT_DIRECTORY, EV_CVS)
    with open(filename, "w") as f:
        f.write(header_line + "\n")
        f.write("\n".join(hand_list))


def gui_test():
    filename = os.path.join(
        DEFAULT_REPORT_DIRECTORY, PICKLE_INFOS)
    with open(filename, "rb") as f:
        hand_lists = pickle.load(f)
        total_results = pickle.load(f)
        action_results = pickle.load(f)
        actions = pickle.load(f)
        board = pickle.load(f)
    filter_view = "MADE_HANDS"
    rows = get_view_list("MADE_HANDS", board)
    rows = get_view_list("RANKS", board)
    column = get_view_list("DRAWS_BLOCKERS", board)
    column = get_view_list("SUITS", board)

    filter_by_ev = None
    filter_ev_condition = EV_TRESHOLD
    data, _, _ = read_data(actions, board, filter_view)
    filter_item = view_item_to_str(get_view_list(filter_view, board)[8])
    # filter_item="other"
    # update_plot(data,actions,filter_item,filter_by_ev,filter_ev_condition,rows,column,True,True)
    update_plot(data, actions, filter_item, filter_by_ev, filter_ev_condition, rows, column, False, False)


if (__name__ == '__main__'):
    gui_test()

