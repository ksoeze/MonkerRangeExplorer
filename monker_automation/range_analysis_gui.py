#!/usr/bin/env python3
import logging
import os
import pickle
import sys
import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

from monker_automation.utils import *

from monker_automation.range_analysis import read_data,update_plot,get_view_list

import numpy as np
import seaborn as sns

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from matplotlib.figure import Figure

class OutputFrame(tk.Frame):
    def __init__(self,root,figure):
        tk.Frame.__init__(self, root)
        self.canvas = FigureCanvasTkAgg(figure,master=root)
        self.canvas.draw()
        #self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        #self.canvas.get_tk_widget().grid(row=0,column=0)

        toolbar = NavigationToolbar2Tk(self.canvas, root)
        toolbar.update()

        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        #self.canvas.get_tk_widget().grid(row=0,column=0)

    def update_figure(self,figure):
        self.canvas.figure=figure
        self.canvas.draw()

class InputLine(tk.Frame):
    def __init__(self,root,label_text,combo_box_list,exclude_checkbox=False):
        tk.Frame.__init__(self, root)
        self.lable=tk.Label(self,
                                   text=label_text,
                                   font=ANALYSIS_FONT,
                            width=20)
        self.comboboxvar = tk.StringVar()
        self.combobox = ttk.Combobox(self, textvariable=self.comboboxvar,values=combo_box_list,font=ANALYSIS_FONT,width=20,state="readonly")
        self.lable.grid(row=0,column=0)
        self.combobox.grid(row=0,column=1)
        self.is_checkbox=exclude_checkbox

        if self.is_checkbox:
            self.checkboxvar = tk.BooleanVar()
            self.checkbox = ttk.Checkbutton(self, text='Exclude', variable=self.checkboxvar)
            self.checkboxvar.set(EXCLUDE_DEFAULT)
            self.checkbox.grid(row=0,column=2)
        for element in self.winfo_children(): element.grid_configure(padx=5, pady=5)

    def get_current_state(self):
        combobox = self.comboboxvar.get()
        if self.is_checkbox:
            checkbox = self.checkboxvar.get()
        else:
            checkbox = EXCLUDE_DEFAULT
        return (combobox, checkbox)

class InputFrame(tk.Frame):
    def __init__(self,root,hand_category_list,filter_by_ev_list,update_function):
        tk.Frame.__init__(self, root)
        self.root = root
        self.update_function=update_function
        self.hand_category=InputLine(root,"Made Hand Category:",hand_category_list)
        self.filter_by_ev=InputLine(root,"Filter by delta EV:",filter_by_ev_list)
        self.filter_by_ev_condition=InputLine(root,"Filter EV Condition:",EV_FILTER_CONDITION)
        self.row_view=InputLine(root,"Row View",RANGE_ANALYSIS_VIEW_TYPES,True)
        self.column_view=InputLine(root,"Column View",RANGE_ANALYSIS_VIEW_TYPES,True)

        #s = ttk.Style()
        #s.configure('button', font=ANALYSIS_FONT)
        self.button = tk.Button(root, text='Update', font=ANALYSIS_FONT, command=self.update_fig)
        self.set_defaults(hand_category_list,filter_by_ev_list)

        self.hand_category.grid(row=0,column=0,sticky="W",padx=1,pady=5)
        self.filter_by_ev.grid(row=1,column=0,sticky="W",padx=1,pady=5)
        self.filter_by_ev_condition.grid(row=2,column=0,sticky="W",padx=1,pady=5)
        self.row_view.grid(row=3,column=0,sticky="W",padx=1,pady=5)
        self.column_view.grid(row=4,column=0,sticky="W",padx=1,pady=5)
        self.button.grid(row=5, column=0,padx=1,pady=5)

        self.table_frame=tk.Frame(root, padx=15, pady=15)
        self.load_image(self.table_frame,TABLE_PNG_NAME)
        self.table_frame.grid(row=6, column=0, columnspan=1, sticky="W")

        self.strat_frame=tk.Frame(root, padx=15, pady=15)
        self.load_image(self.strat_frame,STRATEGY_PNG_NAME)
        self.strat_frame.grid(row=7, column=0, columnspan=1, sticky="W")

    def set_defaults(self,hand_category_list,filter_by_ev_list):
        self.row_view.combobox.set(RANGE_ANALYSIS_VIEW_TYPES[0])
        self.column_view.combobox.set(RANGE_ANALYSIS_VIEW_TYPES[2])
        self.hand_category.combobox.set(hand_category_list[0])
        self.filter_by_ev.combobox.set(filter_by_ev_list[0])
        self.filter_by_ev_condition.combobox.set(EV_FILTER_CONDITION[0])


    def get_infos(self):
        hand_category = self.hand_category.get_current_state()
        ev_selection = (self.filter_by_ev.get_current_state()[0],int(self.filter_by_ev_condition.get_current_state()[0]))
        row = self.row_view.get_current_state()
        column = self.column_view.get_current_state()
        return {
            "category":hand_category,
            "ev":ev_selection,
            "row":row,
            "column":column
        }

    def update_fig(self):
        self.update_function(self.get_infos())

    def load_image(self,frame,img_name):
        filename = os.path.join(
            DEFAULT_REPORT_DIRECTORY, img_name)
        load = Image.open(filename)
        load = load.resize((650,550))
        render = ImageTk.PhotoImage(load,size=(2,2))
        img = tk.Label(frame, image=render)
        img.image = render
        img.grid(row=0, column=0, sticky="W")

class HandQuizFrame(tk.Frame):
    pass




if (__name__ == '__main__'):

    logger = logging.getLogger()
    logger.setLevel("INFO")
    filename = os.path.join(
    DEFAULT_REPORT_DIRECTORY, PICKLE_INFOS)
    with open(filename, "rb") as f:
        hand_lists = pickle.load(f)
        total_results = pickle.load(f)
        action_results = pickle.load(f)
        actions = pickle.load(f)
        board = pickle.load(f)

    data, made_hand_filter, ev_filter = read_data(actions,board,"MADE_HANDS")


    def get_fig(infos):
        filter_item=infos["category"][0]
        filter_by_ev=infos["ev"][0]
        filter_ev_condition=infos["ev"][1]
        rows=get_view_list(infos["row"][0],board)
        column=get_view_list(infos["column"][0],board)
        row_exclude =infos["row"][1]
        column_exclude = infos["column"][1]
        figure = update_plot(data,actions,filter_item,filter_by_ev,filter_ev_condition,rows,column,row_exclude,column_exclude)
        return figure

    def update_output(infos):
        fig = get_fig(infos)
        output.update_figure(fig)

    root = tk.Tk()
    root.title("Range Analysis")
    input_frame = tk.Frame(root)
    input = InputFrame(input_frame,["any"]+made_hand_filter+["other"],["NO"]+ev_filter,update_output)
    input_frame.grid(row=0,column=0,sticky='N')


    output_frame = tk.Frame(root)
    output=OutputFrame(output_frame,get_fig(input.get_infos()))
    output_frame.grid(row=0,column=1)

    def on_closing():
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    #sys.exit()