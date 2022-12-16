"""
Created on Mon Dec  9 14:29:36 2022

@author: gengxiaoyuan
"""

import tkinter as tk
from tkinter import filedialog as fd
from gui import *
#from PIL import Image, ImageTk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


window = tk.Tk()
window.title("Signal Characteristics Graph Generator")
window.rowconfigure(0, minsize=600, weight=1)
window.columnconfigure(1, minsize=800, weight=1)


# save file function
def save_file():
    """Save the current file as a new file."""
    filepath = fd.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return



# left side
frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
frm_buttons.grid(row=0, column=0, sticky="ns")
btn_save = tk.Button(frm_buttons, text="Save As",command=save_file)
btn_save.grid(row=1, column=0, sticky="ew", padx=2, pady=3)



# dataframe input
input_area = tk.Frame(window)
input_area.grid(row=0, column=1, sticky="ns")
#input_area.rowconfigure(0, weight=1)
#input_area.columnconfigure(0, weight=1)

flow1_label = tk.Label(input_area, text="Arm1 flow (pcu/h)")
flow1_label.grid(row=0, column=1)
flow1_input = tk.Entry(input_area)
flow1_input.grid(row=0, column=2)
flow2_label = tk.Label(input_area, text="Arm2 flow (pcu/h)")
flow2_label.grid(row=1, column=1)
flow2_input = tk.Entry(input_area)
flow2_input.grid(row=1, column=2)
flow3_label = tk.Label(input_area, text="Arm3 flow (pcu/h)")
flow3_label.grid(row=2, column=1)
flow3_input = tk.Entry(input_area)
flow3_input.grid(row=2, column=2)
flow4_label = tk.Label(input_area, text="Arm4 flow (pcu/h)")
flow4_label.grid(row=3, column=1)
flow4_input = tk.Entry(input_area)
flow4_input.grid(row=3, column=2)
num_lan1_label = tk.Label(input_area, text="Number of lanes on Arm 1(2)")
num_lan1_label.grid(row=4, column=1)
num_lan1_input = tk.Entry(input_area)
num_lan1_input.grid(row=4, column=2)
num_lan2_label = tk.Label(input_area, text="Number of lanes on Arm 3(4)")
num_lan2_label.grid(row=5, column=1)
num_lan2_input = tk.Entry(input_area)
num_lan2_input.grid(row=5, column=2)
velocity_label = tk.Label(input_area, text="velocity (km/h) (choose from 25, 35, 45)")
velocity_label.grid(row=6, column=1)
velocity_input = tk.Entry(input_area)
velocity_input.grid(row=6, column=2)
which_intersect_label = tk.Label(input_area, text="Which intersect to plot? \
                                    choose from 1, 2, 3, 4 (same number for flow) ",
                                    wraplength = 150, justify = 'left')
which_intersect_label.grid(row=7, column=1)
which_intersect_input = tk.Entry(input_area)
which_intersect_input.grid(row=7, column=2)



def clearInput():
    flow1_input.delete(0, tk.END)
    flow2_input.delete(0, tk.END)
    flow3_input.delete(0, tk.END)
    flow4_input.delete(0, tk.END)
    num_lan1_input.delete(0, tk.END)
    num_lan2_input.delete(0, tk.END)
    velocity_input.delete(0, tk.END)
    which_intersect_input.delete(0, tk.END)

clear_btn = tk.Button(frm_buttons, text='Clear input', command=clearInput)
clear_btn.grid(row=2, column=0)



# plot

def createNewWindow():
    newWindow = tk.Toplevel(window)
    newWindow.rowconfigure(0, minsize=450, weight=1)
    newWindow.columnconfigure(1, minsize=1200, weight=1)

    q0 = int(flow1_input.get())
    q1 = int(flow2_input.get())
    q2 = int(flow3_input.get())
    q3 = int(flow4_input.get())
    v = int(velocity_input.get())
    nol1 = int(num_lan1_input.get())
    nol2 = int(num_lan2_input.get())
    j = int(which_intersect_input.get())
    signal_df = Cap_df(q0, q1, q2, q3, v, nol1, nol2)

    # whether capacity can be output
    if signal_df['Cap'][0] < max(signal_df['q'][0], signal_df['q'][2]) \
        or signal_df['Cap'][1] < max(signal_df['q'][1], signal_df['q'][3]):

        warning_label = tk.Label(newWindow, text="Error occurred: check to make sure all roads are not oversaturated. \
        Make sure the capacity of a road is greater than or equal to the max flow rate on the road", \
        font=("Arial", 25),
        width = 80,
        height = 30,
        wraplength = 200,
        justify = 'left').pack(pady=(0, 0))


    else:
        Coe = df_plot(signal_df, v, j)
        j = j-1

        # plot both directions
        figure1, (ax1, ax2) = plt.subplots(1,2, figsize=(30,8))
        fig1 = FigureCanvasTkAgg(figure1, newWindow)
        fig1.get_tk_widget().pack(side=tk.LEFT)
        # qk curves
        x1 = np.array([0, Coe['kf'][j], Coe['kc'][j], Coe['kj'][j]])
        y1 = np.array([0, Coe['q'][j], Coe['Cap'][j], 0])
        ax1.plot(x1, y1)
        ax1.set_xlabel('Density', fontsize=12)
        ax1.set_xlim(0, max(x1))
        ax1.set_ylim(0, max(y1))
        ax1.set_ylabel('Flow', fontsize=12)
        ax1.set_title("Flow vs Density of Direction %s" % (j+1), fontsize=12)

        # state diagram
        ax2.plot(np.array([Coe['t1'][j], Coe['t2'][j]]), np.array([0, 0]), 'r')
        ax2.plot(np.array([Coe['t1'][j], Coe['t3'][j]]), np.array([0, Coe['x1'][j]]), 'k')
        ax2.plot(np.array([Coe['t2'][j], Coe['t3'][j]]), np.array([0, Coe['x1'][j]]), 'k')
        ax2.plot(np.array([Coe['t1'][j], Coe['t1'][j] + 0.005]), np.array([0, Coe['x2'][j]]), 'k')
        ax2.plot(np.array([Coe['t2'][j], Coe['t2'][j] + 0.005]), np.array([0, Coe['x3'][j]]), 'k')
        ax2.plot(np.array([Coe['t3'][j], Coe['t3'][j] + 0.005]), np.array([Coe['x1'][j], Coe['x4'][j]]), 'k')
        ax2.set_xlim(Coe['t1'][j], Coe['t3'][j] + 0.005)
        ax2.set_ylim(Coe['x1'][j], Coe['x2'][j])
        ax2.set_xlabel('Time(hr)', fontsize=12)
        ax2.set_ylabel('Distance(ft)', fontsize=12)
        ax2.set_title("State Diagram of Direction %s" % (j+1), fontsize=12)

    return figure1



# plot button
plot_button = tk.Button(input_area,
              text="plot",
              command=createNewWindow)
plot_button.grid(row=9, column=2)



# diagram
img_gif = tk.PhotoImage(file = 'intersection.gif')
#img = img_gif.subsample(150, 150)
img = img_gif.subsample(3)
label_img = tk.Label(input_area, image = img, borderwidth=0, highlightthickness=0)
label_img.grid(row = 10, column = 1, sticky="ns",
       columnspan = 5, rowspan = 5, padx=5, pady=5)

input_area.rowconfigure(10, weight=50)


window.mainloop()