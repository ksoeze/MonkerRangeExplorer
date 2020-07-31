#!/usr/bin/env python3
import pickle
import re

from monker_automation.utils import *
import os
import logging
import itertools
import pandas as pd
import timeit
import time
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from monker_automation.views import get_view
from monker_automation.range import hand_in_range, view_item_to_str

def create_regex_from_item(item):
    if len(item) == 1:
        pattern = item
    elif len(item) == 2:
        if item[0] in RANKS and item[1] in SUITS:  # flushblocker
            pattern = item
        else:
            pattern = item[0] + ".+" + item[1]
    elif len(item) == 3:
        if item[0] in RANKS and item[1] in SUITS and item[2] in SUITS:  # specific flush (2nd entry is for cases with "AsKsXdXd in Kss)
            pattern = "(" + item[0] + item[1] + ".+" + item[2] + ")|(" + item[2] + ".*" + item[0] + item[1] + ")"
        elif item[0] in RANKS and item[1] in RANKS and item[2] in RANKS:  # oesd/wrap stuff
            pattern = item[0] + ".+" + item[1] + ".+" + item[2]
    elif len(item) == 4:  # wrap or str flush
        if item[0] in RANKS and item[1] in RANKS and item[2] in RANKS and item[3] in RANKS:
            pattern = item[0] + ".+" + item[1] + ".+" + item[2] + ".+" + item[3]
        elif item[0] in RANKS and item[1] in SUITS and item[2] in RANKS and item[3] in SUITS:
            pattern = item[0] + item[1] + ".+" + item[2] + item[3]
    return "(" + pattern + ")"

def create_regex_from_view(view_list):
    if type(view_list[0]) != str:
        print("Only simple views supported for now")
        return re.compile("XXXX")
    pattern = "|".join([create_regex_from_item(x) for x in view_list])
    return re.compile(pattern)

def get_conditional_sum(data,action,prefix_row, prefix_column,item_row,item_column):
    if item_row == "total" and item_column == "total":
        sum = data[action + " Weight"].sum()
    elif item_row == "total":
        sum = data.loc[data[prefix_column+item_column]==True,action + " Weight"].sum() #TODO eval / debug
    elif item_column == "total":
        sum = data.loc[data[prefix_row+item_row]==True,action + " Weight"].sum()
    else:
        sum = data.loc[(data[prefix_row+item_row]==True) & (data[prefix_column+item_column]==True),action + " Weight"].sum()
    return sum

def heatmap(actions, data, row_list, column_list, exclude_row=True, exclude_column=True):
    # create axes and fill data list with view infos
    if exclude_row:
        row_index=["total"]+[view_item_to_str(x) for x in row_list]+["other"]
        temp_data=add_view_info(data,row_list,"ROW",True)
    else:
        row_index=["total"]+[view_item_to_str(x) for x in row_list]
        temp_data=add_view_info(data,row_list,"ROW",False)
    if exclude_column:
        column_index=["total"]+[view_item_to_str(x) for x in column_list]+["other"]
        temp_data=add_view_info(temp_data,column_list,"COLUMN",True)
    else:
        column_index=["total"]+[view_item_to_str(x) for x in column_list]
        temp_data=add_view_info(temp_data,column_list,"COLUMN",False)
    # one heatmap for every action
    heat_map={}
    for action in actions:
        heat_map[action] = pd.DataFrame(index=row_index,columns=column_index)
        for row in row_index:
            for col in column_index:
                heat_map[action][col][row]=get_conditional_sum(temp_data,action,"ROW", "COLUMN",row,col)
    return heat_map

def cut_lable(label):
    if len(label._text) > MAX_LABEL_LENGTH:
        label._text = label._text[:MAX_LABEL_LENGTH]+"..."
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
    #sns.set()

    # print frequencies
    #heat_map[action]=heat_map[action].replace(to_replace=0,value=np.nan)
    heat_map_draw=(heat_map[action].div(heat_map_total))*100
    #heat_map[action]=heat_map[action].replace(to_replace=0,value=np.nan)
    #heat_map_draw=heat_map_draw.round(decimals=0)

    g = sns.heatmap(heat_map_draw.iloc[::-1].fillna(value=np.nan),annot=True,
                    yticklabels = 1,linewidths=1,cmap=color,
                    ax=axs[subplot_row][0],vmin=0, vmax=100,fmt=".0f")
    axs[subplot_row][0].title.set_text(action + " frequencies " + title)
    g.set_yticklabels([cut_lable(x) for x in g.get_yticklabels()] ,rotation=0)
    g.set_xticklabels([cut_lable(x) for x in g.get_xticklabels()] ,rotation=80)

    # print weights
    heat_map_draw=heat_map[action].div(heat_map[action]["total"]["total"])*100
    #heat_map_draw=heat_map_draw.round(decimals=3)

    g = sns.heatmap(heat_map_draw.iloc[::-1].fillna(value=np.nan),annot=True,
                    yticklabels = 1,linewidths=1,cmap=color,
                    ax=axs[subplot_row][1],vmin=0, vmax=100,fmt=".1f")
    axs[subplot_row][1].title.set_text(action + " range distribution in % " + title)
    g.set_yticklabels([cut_lable(x) for x in g.get_yticklabels()] ,rotation=0)
    g.set_xticklabels([cut_lable(x) for x in g.get_xticklabels()] ,rotation=80)

def plot(heat_map,actions,title,subtitle_infos):
    fig, axs = plt.subplots(nrows=len(actions),ncols=2,figsize=(15,21))
    fig.subplots_adjust(top=0.95, bottom=0.05, left=0.2, right=1, hspace=0.4,
                    wspace=0.4)
    fig.suptitle(title)
    row = 0
    for action in actions:
        plot_action(axs,heat_map,action,subtitle_infos[action],row)
        row+=1
    return fig, axs

def add_view_info(data,view_list,prefix,exclude=True):
    if exclude:
        data[prefix] = False
        for view in view_list:
            pattern=create_regex_from_view(view)
            data[prefix + view_item_to_str(view)] = data["Hand"].apply( lambda row: bool(re.search(pattern,row)))
            #remove true values from this column if it has been matched before...probably possible in one step above?
            data[prefix + view_item_to_str(view)] = data[prefix + view_item_to_str(view)] & ~data[prefix]
            #propagate new matches to total match column
            data[prefix] = data[prefix] | data[prefix + view_item_to_str(view)]
        data[prefix+"other"] = ~data[prefix] #other hands are all hands not matched so far
    else:
        for view in view_list:
            pattern=create_regex_from_view(view)
            data[prefix + view_item_to_str(view)] = data["Hand"].apply( lambda row: bool(re.search(pattern,row)))
    return data

# def get_max_ev_hands(data,actions):
#     #determines the 2 most common actions and returns top 10% of high ev and low ev hands for an action
#     action_weight=[]
#     for action in actions:
#         weight= data[action + " Weight"].sum()
#         action_weight.append((action,weight))
#     action_weight.sort(key=lambda item:item[1],reverse=True)
#     action_weight=[x[0] for x in action_weight[:2]]
#     ev_diff_coln=action_weight[0] + " vs " + action_weight[1]
#     data[ev_diff_coln]=data[action_weight[0] + " EV"] - data[action_weight[1] + " EV"]
#     max_ev=data[ev_diff_coln].max()
#     min_ev=data[ev_diff_coln].min()
#     results={}
#     results[action_weight[0]]= data.drop(data[data[ev_diff_coln]<max_ev*(1-EV_TRESHOLD)].index).sort_values(by=ev_diff_coln)
#     results[action_weight[1]]= data.drop(data[data[ev_diff_coln]>min_ev*(1-EV_TRESHOLD)].index).sort_values(by=ev_diff_coln,ascending=False)
#     return results, action_weight

# def print_data_frame(data,title,filename=None):
#     if filename:
#         filename = os.path.join(
#             DEFAULT_REPORT_DIRECTORY, filename)
#         data.round(2).to_csv(filename,index=False)
#     else:
#         print("-" * 60)
#         print("-" * 60)
#         print(title)
#         #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#         print(data.to_string(index=False))
#         print("-" * 60)
#         print("-" * 60)

def get_view_list(view_type,board):
    if view_type in VIEW_TYPES:
        return get_view(board,view_type)
    if view_type == "RANKS":
        return RANKS
    if view_type == "SUITS":
        return SUITS
    logging.error("View Type not supported ({})".format(view_type))
    return []

def read_data(actions,board,filter_view):
    action_combinations = itertools.combinations(actions,2)
    action_combinations = list(action_combinations)
    hand_infos= pd.DataFrame()
    for action in actions:
        file_name = os.path.join(RANGE_FOLDER, action + ".csv")
        action_info = pd.read_csv(file_name)
        action_info.columns = ['Hand', action + ' Weight', action + ' EV']
        if hand_infos.empty:
            hand_infos=action_info
        else:
            hand_infos=hand_infos.merge(action_info)
    # clean up low weight
    hand_infos['Total Weight']= sum([hand_infos[x+" Weight"] for x in actions])
    hand_infos.drop(hand_infos[hand_infos['Total Weight']<MIN_WEIGHT].index,inplace=True)
    for combination in action_combinations:
        hand_infos[combination[0] + " vs " + combination[1]]=hand_infos[combination[0]+ " EV"] - hand_infos[combination[1]+" EV"]
    view = get_view_list(filter_view,board)
    hand_infos = add_view_info(hand_infos,view,"",True)
    action_combinations = [x[0] + " vs " + x[1] for x in action_combinations]
    view = [view_item_to_str(x) for x in view]
    return hand_infos, view, action_combinations

def get_ev_filtered_data(data,actions,filter_by_ev, ev_condition):
    filtered_actions = filter_by_ev.split(" vs ")
    data = data.sort_values(by=filter_by_ev,ascending = False)
    while len(data) < ev_condition * 2:
        logging.info("Too little hands in range...cut by half")
        ev_condition = ev_condition // 2
    if data.loc[data.index[ev_condition], filter_by_ev] < 0:
        logging.info("Restrict EV condition to less hands {}".format(data.loc[data.index[ev_condition], filter_by_ev]))
    if data.loc[data.index[-ev_condition], filter_by_ev] > 0:
        logging.info("Restrict EV condition to less hands {}".format(data.loc[data.index[ev_condition], filter_by_ev]))
    new_data=data.tail(ev_condition)
    new_data = new_data.append(data.head(ev_condition))
    return filtered_actions,new_data

def update_plot(data,actions,filter_item,filter_by_ev,ev_condition,row_view,column_view,row_exclude=True,column_exclude=True):
    # TODO get total weights and relative weights and show info somehow
    # TODO implement filter
    # TODO implement filter by ev -- DONE but hand condition often not suitable
    # TODO handle subtitle infos
    if filter_item !="" and filter_item != "any":
        data = data.drop(data[data[filter_item]!= True].index)

    if filter_by_ev != "NO":
        actions, data = get_ev_filtered_data(data,actions,filter_by_ev,ev_condition)


    sns.set()
    heat=heatmap(actions,data,row_view,column_view,row_exclude,column_exclude)
    subtitle_infos={}
    for action in actions:
        subtitle_infos[action]=" (total combos: {:.0f})".format(heat[action]["total"]["total"])
    title= "Combos in Range {:.0f}".format(sum([x["total"]["total"] for x in heat.values()]))
    if filter_item !="":
        title+=" (filtered for: {})".format(filter_item)
    fig, axs = plot(heat,actions,title,subtitle_infos)
    return fig
    #plt.show()


# def process_hand_list(actions,board):
#     action_combinations = itertools.combinations(actions,2)
#     action_combinations = list(action_combinations)
#     hand_infos= pd.DataFrame()
#     for action in actions:
#         file_name = os.path.join(RANGE_FOLDER, action + ".csv")
#         action_info = pd.read_csv(file_name)
#         action_info.columns = ['Hand', action + ' Weight', action + ' EV']
#         if hand_infos.empty:
#             hand_infos=action_info
#         else:
#             hand_infos=hand_infos.merge(action_info)
#     # clean up low weight
#     hand_infos['Total Weight']= sum([hand_infos[x+" Weight"] for x in actions])
#     hand_infos.drop(hand_infos[hand_infos['Total Weight']<MIN_QUIZ_WEIGHT].index,inplace=True)
#     for combination in action_combinations:
#         hand_infos[combination[0] + " vs " + combination[1]]=hand_infos[combination[0]+ " EV"] - hand_infos[combination[1]+" EV"]
#     print_data_frame(hand_infos," ",EV_CVS)
#     high_ev_data, ev_actions = get_max_ev_hands(hand_infos,actions)
#     print_data_frame(high_ev_data[ev_actions[0]][["Hand",ev_actions[0]+ " vs " + ev_actions[1]]],"Highest EV {} vs {}".format(ev_actions[0],ev_actions[1]))
#     print_data_frame(high_ev_data[ev_actions[1]][["Hand",ev_actions[0]+ " vs " + ev_actions[1]]],"Lowest EV {} vs {}".format(ev_actions[0],ev_actions[1]))
#     action_1_heat, _ = create_heatmap(ev_actions[:1],high_ev_data[ev_actions[0]],HEAT_ENTRIES_Y,HEAT_ENTRIES_X)
#     action_2_heat, _ = create_heatmap(ev_actions[-1:], high_ev_data[ev_actions[1]], HEAT_ENTRIES_Y, HEAT_ENTRIES_X)
#
#     heat = {}
#     heat[ev_actions[0]]=action_1_heat[ev_actions[0]].div(action_1_heat[ev_actions[0]]["total"]["total"])
#     heat[ev_actions[1]]=action_2_heat[ev_actions[1]].div(action_2_heat[ev_actions[1]]["total"]["total"])
#     show_heatmap(heat,ev_actions,
#                  "Top {}% of EV difference between the two most common actions (Weights in Range)".format(EV_TRESHOLD*100),
#                  {ev_actions[0]:high_ev_data[ev_actions[0]].shape[0],ev_actions[1]:high_ev_data[ev_actions[1]].shape[0]})
#
#     now=time.time()
#     heat_map,heat_map_total=create_heatmap(actions,hand_infos,HEAT_ENTRIES_Y,HEAT_ENTRIES_X)
#     then=time.time()
#     print("Heatmap std {}".format(then-now))
#
#
#     num_hands={}
#     for action in actions:
#         heat_map[action]=heat_map[action].div(heat_map_total)
#         num_hands[action] = hand_infos.shape[0]
#     show_heatmap(heat_map,actions,
#                  "Action Frequencies overall and holding certain cards",
#                  num_hands)
#     view_1=get_view(board,"MADE_HANDS")
#     view_2=get_view(board,"BLOCKERS")
#
#     now = time.time()
#     heat_map, heat_map_total=create_heatmap_from_view(actions,hand_infos,view_1,view_2)
#     then = time.time()
#     print("Heatmap view old {}".format(then-now))
#
#     now = time.time()
#     hand_infos = add_view_info(hand_infos, view_1, "VIEW_ONE ")
#     hand_infos = add_view_info(hand_infos, view_2, "VIEW_TWO ")
#     then = time.time()
#     print("View processing new {}".format(then-now))
#
#     num_hands={}
#     for action in actions:
#         heat_map[action]=heat_map[action].div(heat_map_total)
#         num_hands[action] = hand_infos.shape[0]
#     show_heatmap(heat_map,actions,
#                   "Action Frequencies overall and holding certain cards",
#                   num_hands)
#     high_ev_data, ev_actions = get_max_ev_hands(hand_infos,actions)
#     action_1_heat, _ = create_heatmap_from_view(ev_actions[:1],high_ev_data[ev_actions[0]],view_1,view_2)
#     action_2_heat, _ = create_heatmap_from_view(ev_actions[-1:], high_ev_data[ev_actions[1]], view_1, view_2)
#     heat = {}
#     heat[ev_actions[0]]=action_1_heat[ev_actions[0]].div(action_1_heat[ev_actions[0]]["total"]["total"])
#     heat[ev_actions[1]]=action_2_heat[ev_actions[1]].div(action_2_heat[ev_actions[1]]["total"]["total"])
#     show_heatmap(heat,ev_actions,
#                   "Top {}% of EV difference between the two most common actions (Weights in Range)".format(EV_TRESHOLD*100),
#                   {ev_actions[0]:high_ev_data[ev_actions[0]].shape[0],ev_actions[1]:high_ev_data[ev_actions[1]].shape[0]})
#     plt.show()

def print_ev_differences(self):
    action_combinations = itertools.combinations([i for i in range(len(self.actions))],2)
    action_combinations = list(action_combinations)
    delim=";"
    header_line="Hand"+delim
    for action in self.actions:
        header_line+=action + delim
        header_line+="EV " + action + delim
    for combo in action_combinations:
        header_line+="EV diff " + self.actions[combo[0]] + " " + self.actions[combo[1]] + delim
    hand_list=[]
    for hand in self.overall_data:
        hand_line=hand["hand"]+delim
        for action in hand["actions"]:
            hand_line+="{0:.0f}%".format(action[0]/hand["total_weight"]*100)+delim
            hand_line+="{0:.2f}".format(action[1]/1000)+delim
        for combo in action_combinations:
            hand_line+="{0:.3f}".format((hand["actions"][combo[0]][1]-hand["actions"][combo[1]][1])/1000)+delim
        hand_list.append(hand_line)
    filename = os.path.join(
        DEFAULT_REPORT_DIRECTORY, EV_CVS)
    with open(filename, "w") as f:
        f.write(header_line+"\n")
        f.write("\n".join(hand_list))
#
# def asdf():
#     filename = os.path.join(
#     DEFAULT_REPORT_DIRECTORY, PICKLE_INFOS)
#     with open(filename, "rb") as f:
#         hand_lists = pickle.load(f)
#         total_results = pickle.load(f)
#         action_results = pickle.load(f)
#         actions = pickle.load(f)
#         board = pickle.load(f)
#     process_hand_list(actions,board)
#     view_1=get_view(board,"DRAWS_BLOCKERS")
#     now=time.time()
#     for view in view_1:
#         for item in hand_lists[0][1]:
#             hand_in_range(item[0],view)
#     then=time.time()
#     print(then-now)
#
#     now=time.time()
#     for view in view_1:
#         pattern=create_regex_from_view(view)
#         for item in hand_lists[0][1]:
#             bool(re.search(pattern,item[0]))
#     then=time.time()
#     print(then-now)

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
    column=get_view_list("DRAWS_BLOCKERS",board)
    column=get_view_list("SUITS",board)

    filter_by_ev=None
    filter_ev_condition=EV_TRESHOLD
    data, _, _ = read_data(actions,board,filter_view)
    filter_item=view_item_to_str(get_view_list(filter_view,board)[8])
    #filter_item="other"
    #update_plot(data,actions,filter_item,filter_by_ev,filter_ev_condition,rows,column,True,True)
    update_plot(data,actions,filter_item,filter_by_ev,filter_ev_condition,rows,column,False,False)

if (__name__ == '__main__'):
    gui_test()
    #asdf()
