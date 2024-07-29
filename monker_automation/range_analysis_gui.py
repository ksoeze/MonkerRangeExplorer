#!/usr/bin/env python3
import logging
import os
import pickle
#from timebudget import timebudget
import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

from monker_automation.utils import *

from monker_automation.range_analysis import read_data, update_plot, get_view_list, get_quiz_hand
from monker_automation.hand_quiz import InputFrame as QuizFrame

import matplotlib

matplotlib.use('svg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # ,NavigationToolbar2Tk


class OutputFrame(tk.Frame):
    def __init__(self, root, figure):
        tk.Frame.__init__(self, root)
        self.canvas = FigureCanvasTkAgg(figure, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_figure(self, figure):
        self.canvas.figure = figure
        self.canvas.draw()


class InputLine(tk.Frame):
    def __init__(self, root, label_text, combo_box_list, exclude_checkbox=False):
        tk.Frame.__init__(self, root)
        self.lable = tk.Label(self,
                              text=label_text,
                              font=ANALYSIS_FONT,
                              width=20)
        self.comboboxvar = tk.StringVar()
        self.combobox = ttk.Combobox(self, textvariable=self.comboboxvar, values=combo_box_list, font=ANALYSIS_FONT,
                                     width=20, state="readonly")
        self.lable.grid(row=0, column=0)
        self.combobox.grid(row=0, column=1)
        self.is_checkbox = exclude_checkbox

        if self.is_checkbox:
            self.checkboxvar = tk.BooleanVar()
            self.checkbox = ttk.Checkbutton(self, text='Exclude', variable=self.checkboxvar)
            self.checkboxvar.set(EXCLUDE_DEFAULT)
            self.checkbox.grid(row=0, column=2)

            self.invboxvar = tk.BooleanVar()
            self.invbox = ttk.Checkbutton(self, text='Invert', variable=self.invboxvar)
            self.invboxvar.set(False)
            self.invbox.grid(row=0, column=3)


        for element in self.winfo_children(): element.grid_configure(padx=5, pady=5)

    def get_current_state(self):
        combobox = self.comboboxvar.get()
        if self.is_checkbox:
            checkbox = self.checkboxvar.get()
            invbox = self.invboxvar.get()
        else:
            checkbox = EXCLUDE_DEFAULT
            invbox = False
        return (combobox, checkbox, invbox)


class InputLineFilter(tk.Frame):
    def __init__(self, root, label_text):
        tk.Frame.__init__(self, root)
        self.lable = tk.Label(self,
                              text=label_text,
                              font=ANALYSIS_FONT,
                              width=20)
        self.textinputvar = tk.StringVar()
        self.textinput = ttk.Entry(self, textvariable=self.textinputvar, font=ANALYSIS_FONT, width=20)
        self.lable.grid(row=0, column=0)
        self.textinput.grid(row=0, column=1)
        for element in self.winfo_children(): element.grid_configure(padx=5, pady=5)

    def get_current_state(self):
        return self.textinputvar.get()


class InputFrame(tk.Frame):
    def __init__(self, root, hand_category_list, filter_by_ev_list, update_function):
        tk.Frame.__init__(self, root)
        self.root = root
        self.update_function = update_function

        self.hand_filter = InputLineFilter(root, "Hand Filter:")
        self.hand_filter_exclude = InputLineFilter(root, "Exclude:")
        self.hand_category = InputLine(root, "Made Hand Category:", hand_category_list)
        self.filter_by_ev = InputLine(root, "Filter by delta EV:", filter_by_ev_list)
        self.filter_by_ev_condition = InputLine(root, "Filter EV Condition:", EV_FILTER_CONDITION)
        self.row_view = InputLine(root, "Row View", RANGE_ANALYSIS_VIEW_TYPES, True)
        self.column_view = InputLine(root, "Column View", RANGE_ANALYSIS_VIEW_TYPES, True)

        self.button = tk.Button(root, text='Update', font=ANALYSIS_FONT, command=self.update_fig)
        self.set_defaults(hand_category_list, filter_by_ev_list)

        self.hand_filter.grid(row=0, column=0, sticky="W", padx=1, pady=2)
        self.hand_filter_exclude.grid(row=1, column=0, sticky="W", padx=1, pady=2)
        self.hand_category.grid(row=2, column=0, sticky="W", padx=1, pady=2)
        self.filter_by_ev.grid(row=3, column=0, sticky="W", padx=1, pady=2)
        self.filter_by_ev_condition.grid(row=4, column=0, sticky="W", padx=1, pady=2)
        self.row_view.grid(row=5, column=0, sticky="W", padx=1, pady=2)
        self.column_view.grid(row=6, column=0, sticky="W", padx=1, pady=2)
        self.button.grid(row=7, column=0, padx=1, pady=2)

        self.info_text = tk.StringVar()
        self.infos = tk.Message(root, textvariable=self.info_text, font='TkFixedFont', width=650)
        self.infos.grid(row=8, column=0, padx=1, pady=2, sticky="W")

        self.strat_frame = tk.Frame(root, padx=5, pady=2)
        #self.load_image(self.strat_frame, STRATEGY_PNG_NAME)
        self.strat_frame.grid(row=9, column=0, columnspan=1, sticky="W")
        self.range_frame = tk.Frame(root, padx=5, pady=2)
        #self.load_image(self.range_frame, RANGE_PNG_NAME)
        self.range_frame.grid(row=10, column=0, columnspan=1, sticky="W")

    def set_info_text(self, infos):
        text = "Range total:               {:6.0f} (100%)\n".format(infos["total"])
        text += "after Hand Filter:         {:6.0f} ({:3.0f}%) {}\n".format(infos["filter"],
                                                                            infos["filter"] / infos["total"] * 100,
                                                                            infos["hand_filter_str"])
        text += "after Hand Filter exclude: {:6.0f} ({:3.0f}%) {}\n".format(infos["filter excl"],
                                                                            infos["filter excl"] / infos["total"] * 100,
                                                                            infos["hand_filter_excl_str"])
        text += "after Made Hand Category:  {:6.0f} ({:3.0f}%) {}\n".format(infos["made hand"],
                                                                            infos["made hand"] / infos["total"] * 100,
                                                                            infos["hand_item_str"])
        text += "after EV filter: Combos    {:6.0f} ({:3.0f}%)\n".format(infos["final"],
                                                                         infos["final"] / infos["total"] * 100)
        self.info_text.set(text)

    def set_defaults(self, hand_category_list, filter_by_ev_list):
        if PREFLOP:
            self.row_view.combobox.set(RANGE_ANALYSIS_VIEW_TYPES[11])
        else:
            self.row_view.combobox.set(RANGE_ANALYSIS_VIEW_TYPES[0])
        if PREFLOP:
            self.column_view.combobox.set(RANGE_ANALYSIS_VIEW_TYPES[12])
        else:
            self.column_view.combobox.set(RANGE_ANALYSIS_VIEW_TYPES[3])
        self.hand_category.combobox.set(hand_category_list[0])
        self.filter_by_ev.combobox.set(filter_by_ev_list[0])
        self.filter_by_ev_condition.combobox.set(EV_FILTER_CONDITION[3])

    def get_infos(self):
        hand_category = self.hand_category.get_current_state()
        ev_selection = (
        self.filter_by_ev.get_current_state()[0], int(self.filter_by_ev_condition.get_current_state()[0]))
        row = self.row_view.get_current_state()
        column = self.column_view.get_current_state()
        filter = self.hand_filter.get_current_state()
        filter_exclude = self.hand_filter_exclude.get_current_state()
        return {
            "category": hand_category,
            "ev": ev_selection,
            "row": row,
            "column": column,
            "filter": filter,
            "filter_exclude": filter_exclude
        }

    def update_fig(self):
        self.update_function(self.get_infos())

    def load_image(self, frame, img_name):
        filename = os.path.join(
            DEFAULT_REPORT_DIRECTORY, img_name)
        load = Image.open(filename)
        if LAPTOP:
            load = load.resize((550, 280))
        else:
            load = load.resize((800, 450))
        render = ImageTk.PhotoImage(load)
        img = tk.Label(frame, image=render)
        img.image = render
        img.grid(row=0, column=0, sticky="W")


def start_gui(actions=[],board=""):

    logger = logging.getLogger()
    logger.setLevel("INFO")
    if actions == []:
        filename = os.path.join(
            DEFAULT_REPORT_DIRECTORY, PICKLE_INFOS)
        with open(filename, "rb") as f:
            hand_lists = pickle.load(f)
            total_results = pickle.load(f)
            action_results = pickle.load(f)
            actions = pickle.load(f)
            board = pickle.load(f)
    if PREFLOP:
        board="2s2c2d2h"
        data, made_hand_filter, ev_filter = read_data(actions, board, "PREFLOP_PAIRS_HIGH_CARD")
    else:
        data, made_hand_filter, ev_filter = read_data(actions, board, "MADE_HANDS")



    def get_fig(infos):
        filter_item = infos["category"][0]
        filter_by_ev = infos["ev"][0]
        filter_ev_condition = infos["ev"][1]
        rows = get_view_list(infos["row"][0], board)
        column = get_view_list(infos["column"][0], board)
        row_exclude = infos["row"][1]
        column_exclude = infos["column"][1]
        row_invert = infos["row"][2]
        column_invert = infos["column"][2]
        hand_filter = infos["filter"]
        hand_filter_exclude = infos["filter_exclude"]
        figure, infos = update_plot(data, actions, board, hand_filter, hand_filter_exclude, filter_item, filter_by_ev,
                                    filter_ev_condition, rows, column, row_exclude, column_exclude,row_invert,column_invert)
        return figure, infos


    #@timebudget
    def update_output(infos):
        fig, infos = get_fig(infos)
        output.update_figure(fig)
        input.set_info_text(infos)
        input.load_image(input.strat_frame, STRATEGY_PNG_NAME)
        input.load_image(input.range_frame, RANGE_PNG_NAME)
        plt.close("all")
        # timebudget.report('update_output')


    root = tk.Tk()
    root.title("Range Analysis")
    input_frame = tk.Frame(root)
    input = InputFrame(input_frame, ["any"] + made_hand_filter + ["other"], ["NO"] + ev_filter, update_output)
    input_frame.grid(row=0, column=0, sticky='N')


    def update_quiz(hand, action, index):
        infos = input.get_infos()
        hand, filter_infos = get_quiz_hand(data, actions, board, infos["filter"], infos["filter_exclude"],
                                           infos["category"][0], infos["ev"][0], infos["ev"][1])
        input.set_info_text(filter_infos)
        if hand:
            quiz.set_card_label(hand)


    quiz_frame = tk.Frame(root)
    quiz = QuizFrame(quiz_frame, actions, update_quiz, None)
    infos = input.get_infos()
    hand, filter_infos = get_quiz_hand(data, actions, board, infos["filter"], infos["filter_exclude"],
                                       infos["category"][0], infos["ev"][0], infos["ev"][1])
    if hand:
        quiz.set_card_label(hand)
    quiz_frame.grid(row=1, column=0, sticky='N')

    output_frame = tk.Frame(root)
    fig, infos = get_fig(input.get_infos())
    input.set_info_text(infos)
    input.load_image(input.strat_frame, STRATEGY_PNG_NAME)
    input.load_image(input.range_frame, RANGE_PNG_NAME)
    output = OutputFrame(output_frame, fig)
    output_frame.grid(row=0, column=2, rowspan=2)


    def on_closing():
        root.quit()
        root.destroy()


    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if (__name__ == '__main__'):
    start_gui()