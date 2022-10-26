from ast import Constant, Global
from email.mime import audio
import tkinter
from tkinter import *
from turtle import window_width
from xml.dom import NotFoundErr
from time import sleep
from constants import Constants
from audiothread import audioThread
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np

cBtnName = ""
tRecord = None
isActive = False

def show(self, tinput):
    global cBtnName, tRecord, f_plot1
    print(self.get())
    cBtnName = "" + self.get()
    textDisp()
    tRecord.recording = True
    
    # a = 0
    # while True:
    #     a+=1
    
def addBtn(window, name, left, top, btnW, btnH, text_input):
    var = tkinter.StringVar()
    var.set(name)
    btnE = tkinter.Button(window,text=name,command=lambda:show(var, text_input))
    btnE.place(x=left, y=top, width=btnW,height=btnH)
    return btnE

def addBtnAuto(window, name, left, top, btnW, btnH, cmd):
    var = tkinter.StringVar()
    var.set("Tuning mode - " + name)
    btnE = tkinter.Button(window,text=name,command=cmd)
    btnE.place(x=left, y=top, width=btnW,height=btnH)
    return btnE

def addFrame(window, left, top, w, h):
    frame = tkinter.Frame(window, highlightbackground='gray', highlightthickness=2)  
    frame.place(x=left, y=top, width=w,height=h)

def textDisp():
    global cBtnName
    text_input.configure(state='normal')
    text_input.tag_configure("center", justify='center')
    text = ""
    if autoDetect == True:
        text += "Tuning mode - Manual "
        text += cBtnName
    else:
        text = "Tuning mode - Auto"
    text_input.delete('1.0', '2.0')
    # text_input.insert('insert', text)
    text_input.insert('1.0', text)
    text_input.tag_add("center", "1.0", "end")
    text_input.configure(state='disabled')

def addTextBox(window, left, top, text):
    Font_tuple = ("Terminal", 30, "bold")
    text_input = tkinter.Text(window)
    text_input.configure(font = Font_tuple)
    text_input.insert('insert', text)
    w = 7 * (Constants.BTN_INTERVAL + Constants.BTN_WIDTH) - Constants.BTN_INTERVAL
    text_input.place(x=left, y=top, width = w, height = Constants.BTN_HEIGHT*3//2)
    text_input.configure(background='White', state='disabled')
    return text_input

def initFigure(window):
    global f_plot1, g_plot1, canvas
    fig = Figure(figsize=(6.4, 3.2), dpi=100)
    f_plot1 = fig.add_subplot(211)
    # f_plot1.set_xlim([0, Constants.CHUNK])
    # f_plot1.set_ylim([-1,1])
    f_plot1.grid()
    g_plot1 = fig.add_subplot(212)
    # g_plot1.set_xlim([0, Constants.CHUNK])
    # g_plot1.set_ylim([-1,1])
    g_plot1.grid()
    # t = np.arange(0, 3, .01)
    # ax = fig.add_subplot()
    # # line, = ax.plot(t, 2 * np.sin(2 * np.pi * t))
    # ax.set_xlabel("time [s]")
    # ax.set_ylabel("f(t)")
    canvas = FigureCanvasTkAgg(fig, master=window)  # A tk.DrawingArea.
    # canvas.draw()
    canvas.get_tk_widget().place(x=15, y=15)
    plt.ion()

def updateWin():
    global canvas, window
    canvas.draw()
    canvas.flush_events()
    window.after(100, updateWin)

autoDetect = True

def ifClicked():
    global autoDetect
    if autoDetect == False:
        btnE1.configure(state=NORMAL)
        btnA.configure(state=NORMAL)
        btnD.configure(state=NORMAL)
        btnG.configure(state=NORMAL)
        btnB.configure(state=NORMAL)
        btnE2.configure(state=NORMAL)
        btnAuto.configure(text="Manual")
        autoDetect = True
    else:
        btnE1.configure(state=DISABLED)
        btnA.configure(state=DISABLED)
        btnD.configure(state=DISABLED)
        btnG.configure(state=DISABLED)
        btnB.configure(state=DISABLED)
        btnE2.configure(state=DISABLED)
        btnAuto.configure(text="Auto")
        autoDetect = False
    textDisp()

def addButtons(window, text_input):
    global btnE1, btnA, btnD, btnG, btnB, btnE2, btnAuto
    top = 400
    left = 7 
    btnAuto = addBtnAuto(window, 'Auto', left, top, Constants.BTN_WIDTH, Constants.BTN_HEIGHT, ifClicked)
    left += Constants.BTN_INTERVAL + Constants.BTN_WIDTH
    btnE1 = addBtn(window, 'E1', left, top, Constants.BTN_WIDTH, Constants.BTN_HEIGHT, text_input)
    left += Constants.BTN_INTERVAL + Constants.BTN_WIDTH
    btnA = addBtn(window, 'A', left, top, Constants.BTN_WIDTH, Constants.BTN_HEIGHT, text_input)
    left += Constants.BTN_INTERVAL + Constants.BTN_WIDTH
    btnD = addBtn(window, 'D', left, top, Constants.BTN_WIDTH, Constants.BTN_HEIGHT, text_input)
    left += Constants.BTN_INTERVAL + Constants.BTN_WIDTH
    btnG = addBtn(window, 'G', left, top, Constants.BTN_WIDTH, Constants.BTN_HEIGHT, text_input)
    left += Constants.BTN_INTERVAL + Constants.BTN_WIDTH
    btnB = addBtn(window, 'B', left, top, Constants.BTN_WIDTH, Constants.BTN_HEIGHT, text_input)
    left += Constants.BTN_INTERVAL + Constants.BTN_WIDTH
    btnE2 = addBtn(window,'E2', left, top, Constants.BTN_WIDTH, Constants.BTN_HEIGHT, text_input)

def on_closing():
    global tRecord, window
    tRecord.recording = False
    tRecord.running = False
    tRecord.join(0.3)
    window.destroy()



def initWin(title):
    global text_input, f_plot1, canvas, tRecord, window, g_plot1
    window = tkinter.Tk()
    window.title(title)
    # window.configure(background='Grey')
    initFigure(window)
    maxw, maxh = window.maxsize()
    w = Constants.WIN_WIDTH
    h = Constants.WIN_HEIGHT
    left = maxw//2 - w//2
    top = maxh//2 - h//2
    window.geometry("%dx%d+%d+%d"%(w-30,h,left,top))
    addFrame(window, 49, 340, Constants.WIN_WIDTH-117, 2)
    text_input = addTextBox(window, 7, 350, '')
    addButtons(window, text_input)

    tRecord = audioThread(f_plot1, canvas, g_plot1)
    tRecord.start()

    print(w-190)
    ifClicked()
    textDisp()
    window.resizable(0, 0)
    window.protocol("WM_DELETE_WINDOW", on_closing)
    updateWin()
    window.mainloop()

initWin('Tuner')

