#!/usr/bin/env python3

from monker_automation.utils import *
import os
import pickle
from random import randint
import logging
import itertools

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
#from monker_automation.range_analysis import process_hand_list

class SpotData:

    def __init__(self):
        self.overall_data = []
        self.actions = []
        hand_lists, self.total_results, self.action_results = self.read_infos()
        self.cleanup_data(hand_lists)

    def read_infos(self):
        filename = os.path.join(
            DEFAULT_REPORT_DIRECTORY, PICKLE_INFOS)
        with open(filename, "rb") as f:
            hand_lists = pickle.load(f)
            total_results = pickle.load(f)
            action_results = pickle.load(f)
        return hand_lists, total_results, action_results

    def cleanup_data(self, hand_lists):
        for item in hand_lists:
            self.actions.append(item[0])
            item[1].sort(key=lambda x: x[0])
        total_hands = 0
        total_hands_in_range = 0
        total_hands_valid_freq = 0
        total_hands_valid_ev = 0
        for index in range(len(hand_lists[0][1])):
            # HAND: { "hand":
            #        "total_weight":
            #        "total_ev":
            #        "ev_diff":
            #        "actions":[(weight,ev)..]
            #        "main_action":(weight,index)
            #        }
            hand_info = {
                "hand": hand_lists[0][1][index][0],
                "total_weight": 0,
                "total_ev": 0,
                "ev_diff": 0,
                "actions": [],
                "main_action": (0, 0)
            }
            for action in hand_lists:
                hand_info["total_weight"] += action[1][index][1]
                hand_info["actions"].append(action[1][index][1:])
            total_hands += 1
            if hand_info["total_weight"] > MIN_QUIZ_WEIGHT:
                total_hands_in_range += 1
                hand_info["main_action"] = self.main_freq(hand_info)
                if hand_info["main_action"][0] / hand_info["total_weight"] >= MIN_ACTION_FREQ:
                    total_hands_valid_freq += 1
                    hand_info["total_ev"], hand_info["ev_diff"] = self.get_main_ev(hand_info)
                    if self.valid_ev(hand_info):
                        total_hands_valid_ev += 1
                        self.overall_data.append(hand_info)
        print("Total Hands overall: {}".format(total_hands))
        print("Total Hands in range: {}".format(total_hands_in_range))
        print("Total Hands matching frequency constraints: {}".format(total_hands_valid_freq))
        print("Total Hands matching EV constraints: {}".format(total_hands_valid_ev))
        if not HAND_QUIZ:
            print("WARNING: RUN spot analysis with HAND_QUIZZ == FALSE?? rerun to get correct informations")
        return

    def main_freq(self, hand_info):
        main_action = (0, 0)
        for i in range(len(hand_info["actions"])):
            if hand_info["actions"][i][0] > main_action[0]:
                main_action = (hand_info["actions"][i][0], i)
        return main_action

    def get_main_ev(self, hand_info):
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

    def valid_ev(self, hand_info):
        if hand_info["actions"][0][1] == -float("inf"):
            return True
        if MIN_EV_DIFF * 1000 <= hand_info["ev_diff"] < MAX_EV_DIFF * 1000:
            return True
        else:
            return False

    def get_random_hand(self):
        hand = self.overall_data[randint(0, len(self.overall_data) - 1)]
        return hand

    def print_hand(self, hand):
        output_text = "Hand: {}".format(hand[0])
        for action in zip(self.actions, hand[2:]):
            output_text += " {0}: {1:.0f} EV: {2:.2f} chips".format(action[0], action[1][0] / hand[1] * 100,
                                                                    action[1][1] / 1000)
        print(output_text)
        return output_text

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



class ResultLabel(tk.Frame):
    def __init__(self, root, column, width=10):
        tk.Frame.__init__(self, root)
        self.root = root
        self.frequency = tk.StringVar()
        self.ev = tk.StringVar()
        if width <= 4:
            width = 5
        self.freq_label = tk.Label(root,
                                   textvariable=self.frequency,
                                   padx=5,
                                   pady=2,
                                   width=width,
                                   font=RESULT_FONT)
        self.ev_label = tk.Label(root,
                                 textvariable=self.ev,
                                 padx=5,
                                 pady=2,
                                 width=width,
                                 font=RESULT_FONT)
        self.default_bg = self.freq_label.cget('bg')
        self.freq_label.grid(row=0, column=column)
        self.ev_label.grid(row=1, column=column)

    def set_values(self, hand_info, index):
        self.frequency.set("{0:.0f}%".format(hand_info["actions"][index][0] / hand_info["total_weight"] * 100))
        if hand_info["actions"][index][1] != float("-inf"):
            if hand_info["actions"][index][1]/1000 > 90 or hand_info["actions"][index][1]/1000 < -90:
                self.ev.set("{0:.1f}".format(hand_info["actions"][index][1] / 1000))
            else:
                self.ev.set("{0:.2f}".format(hand_info["actions"][index][1] / 1000))
        self.freq_label.config(background=self.default_bg)

        if index == hand_info["action_chosen"] and index != hand_info["main_action"][1]:
            self.freq_label.config(background="tomato")
        if index == hand_info["main_action"][1]:
            self.freq_label.config(background="white")


class InputFrame(tk.Frame):
    def __init__(self, root, actions, update_output, print_ev_diff):
        self.root = root
        self.actions = actions
        self.update_output = update_output
        self.print_ev_diff = print_ev_diff

        self.card_frame = tk.Frame(root, padx=15, pady=15)
        self.result_frame = tk.Frame(root, padx=15, pady=15)
        self.action_button_frame = tk.Frame(root, padx=15, pady=15)
        self.image_frame = tk.Frame(root, padx=15, pady=15)

        self.card_str_list = [tk.StringVar() for i in range(4)]
        self.card_labels = [tk.Label(self.card_frame,
                                     textvariable=self.card_str_list[i],
                                     padx=2,
                                     font=INFO_FONT) for i in range(4)
                            ]
        for i in range(4):
            self.card_labels[i].grid(row=0, column=i)

        self.result_card_str_list = [tk.StringVar() for i in range(4)]
        self.result_card_frame = tk.Frame(root, padx=15, pady=15)
        self.result_card_labels = [tk.Label(self.result_card_frame,
                                            textvariable=self.result_card_str_list[i],
                                            padx=2,
                                            font=INFO_FONT) for i in range(4)
                                   ]
        for i in range(4):
            self.result_card_labels[i].grid(row=0, column=i)

        self.button_list = [self.create_button(i) for i in range(len(self.actions))]

        self.load_image()
        self.result_label_list = []
        self.current_hand = ""
        self.played_hands = []
        self.image_frame.grid(row=0, column=0, columnspan=2, sticky="W")
        self.card_frame.grid(row=1, column=0)
        self.result_card_frame.grid(row=4, column=0)
        self.action_button_frame.grid(row=1, column=1)

        self.result_label_frame = tk.Frame(root, padx=15, pady=15)
        self.result_label_frame.grid(row=4, column=1)
        self.result_label_list = [ResultLabel(self.result_label_frame, i, len(self.actions[i])) for i in
                                  range(len(self.actions))]
        for i in range(len(self.actions)):
            self.result_label_list[i].grid(row=0, column=i)
        ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=2, sticky="we")
        ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky="we")
        self.sum_button = tk.Button(
            self.image_frame, text="Print Summary",
            command=self.print_summary)
        self.sum_button.config(font=BUTTON_FONT,
                               padx=5, pady=5)
        self.sum_button.grid(row=0, column=1, sticky="S")

    def set_card_label(self, hand):
        self.current_hand = hand
        self.set_label(hand["hand"], zip(self.card_str_list, self.card_labels))

    def set_label(self, hand, labels):
        for string_var, label in labels:
            if len(hand) == 0:
                string_var.set("")
            else:
                card = hand[0:2]
                suit = card[1]
                label.config(foreground=SUIT_COLORS[suit])
                string_var.set(card[0] + SUIT_SIGN_DIC[suit])
                hand = hand[2:]

    def on_button_clicked(self, column):
        def event_handler():
            self.process_button_clicked(column)

        return event_handler

    def create_button(self, column):
        text = self.actions[column]
        button = tk.Button(
            self.action_button_frame, text=text,
            command=self.on_button_clicked(column))
        button.config(font=BUTTON_FONT,
                      padx=5, pady=5)
        button.grid(row=0, column=column)
        return button

    def process_button_clicked(self, column):
        index = column
        action = self.actions[column]
        self.current_hand["action_chosen"] = column
        self.show_solution()
        self.update_output(self.current_hand, action, index)

    def load_image(self):
        filename = os.path.join(
            DEFAULT_REPORT_DIRECTORY, TABLE_PNG_NAME)
        load = Image.open(filename)
        render = ImageTk.PhotoImage(load)
        img = tk.Label(self.image_frame, image=render)
        img.image = render
        img.grid(row=0, column=0, sticky="W")

    def show_solution(self):
        if SHOW_SOLUTION:
            self.set_label(self.current_hand["hand"], zip(self.result_card_str_list, self.result_card_labels))
            for i in range(len(self.actions)):
                self.result_label_list[i].set_values(self.current_hand, i)
        self.played_hands.append(self.current_hand)

    def print_summary(self):
        print("-" * 60)
        print("-" * 60)
        if len(self.played_hands) == 0:
            return
        num_hands = len(self.played_hands)

        gto_actions = [0 for i in range(len(self.actions))]
        my_actions = [0 for i in range(len(self.actions))]
        errors = 0
        ev_difference = 0

        for hand in self.played_hands:
            hand["ev_error"] = 0
            for i in range(len(hand["actions"])):
                gto_actions[i] += hand["actions"][i][0] / hand["total_weight"] / num_hands * 100
                if i == hand["action_chosen"]:
                    my_actions[i] += 1 / num_hands * 100
            if hand["action_chosen"] != hand["main_action"][1]:
                errors += 1
                hand_ev_error = (hand["total_ev"] - hand["actions"][hand["action_chosen"]][1]) / 1000
                hand["ev_error"] = hand_ev_error
                ev_difference += hand_ev_error / num_hands

        if ev_difference != float("inf"):
            print("Printing Hands where you lost more than {} chips".format(PRINT_EV_ERROR))
            self.played_hands.sort(key=lambda x: x["ev_error"])
            for hand in self.played_hands:
                if hand["ev_error"] > PRINT_EV_ERROR:
                    gto_action_str = "{0:.2f}".format(hand["total_ev"] / 1000)
                    gto_action_str += " " * (7 - len(gto_action_str))
                    output_str = "{0}: GTO: {1} EV:{2}".format(hand["hand"],
                                                               self.actions[hand["main_action"][1]] + " " * (11 - len(
                                                                   self.actions[hand["main_action"][1]])),
                                                               gto_action_str)
                    output_str += " YOU: {0} which loses {1:.2f}".format(
                        self.actions[hand["action_chosen"]] + " " * (11 - len(self.actions[hand["action_chosen"]])),
                        hand["ev_error"])
                    print(output_str)
        print("-" * 60)
        print("-" * 60)
        print("You played {} hands".format(num_hands))
        print("You got {0:.0f}% right".format((1 - errors / num_hands) * 100))
        if ev_difference != float("inf"):
            print("You lost {0:.2f} chips per hand".format(ev_difference))
        print("Action Frequencies (GTO | YOU):")
        for i in range(len(self.actions)):
            gto_action_str = "{0:.1f}%".format(gto_actions[i])
            gto_action_str += " " * (5 - len(gto_action_str))
            print("{0} {1} | {2:.1f}%".format(self.actions[i] + " " * (11 - len(self.actions[i])),
                                              gto_action_str,
                                              my_actions[i]))
        print("-" * 60)
        print("-" * 60)

        if SHOW_STRATEGY:
            filename = os.path.join(
              DEFAULT_REPORT_DIRECTORY, STRATEGY_PNG_NAME )
            load = Image.open(filename)
            Image._show(load)
        if EV_RESULTS:
            self.print_ev_diff()
        return

if (__name__ == '__main__'):
    logger = logging.getLogger()
    logger.setLevel("INFO")
    spot_data = SpotData()
    hand = spot_data.get_random_hand()


    def update_output(hand, action, index):
        hand = spot_data.get_random_hand()
        input_frame.set_card_label(hand)
        return

    root = tk.Tk()
    root.title("Hand Quiz")
    input_frame = InputFrame(root, spot_data.actions, update_output, spot_data.print_ev_differences)
    input_frame.set_card_label(hand)
    root.mainloop()
