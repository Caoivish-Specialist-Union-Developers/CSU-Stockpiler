from tkinter import ttk
from PIL import ImageTk, Image
from tkinter import *

from lib.Helpers.nameAndDestroy import NameAndDestroy

def newstockpopup(image, StockpilerWindow):
    # global stockpilename
    global PopupWindow
    global StockpileNameEntry
    root_x = StockpilerWindow.winfo_rootx()
    root_y = StockpilerWindow.winfo_rooty()
    if root_x == root_y == -32000:
        win_x = 100
        win_y = 100
    else:
        win_x = root_x - 20
        win_y = root_y + 125
    location = "+" + str(win_x) + "+" + str(win_y)
    PopupWindow = Toplevel(StockpilerWindow)
    PopupWindow.geometry(location)
    PopupFrame = ttk.Frame(PopupWindow)
    PopupWindow.resizable(False, False)
    PopupFrame.pack()
    PopupWindow.grab_set()
    PopupWindow.focus_force()
    im = Image.fromarray(image)
    tkimage = ImageTk.PhotoImage(im)
    NewStockpileLabel = ttk.Label(
        PopupFrame, text="Looks like a new stockpile.", style="TLabel"
    )
    NewStockpileLabel.grid(row=2, column=0)
    StockpileNameImage = ttk.Label(PopupFrame, image=tkimage, style="TLabel")
    StockpileNameImage.image = tkimage
    StockpileNameImage.grid(row=5, column=0)
    StockpileNameLabel = ttk.Label(
        PopupFrame, text="What is the name of the stockpile?", style="TLabel"
    )
    StockpileNameLabel.grid(row=7, column=0)
    StockpileNameEntry = ttk.Entry(PopupFrame)
    StockpileNameEntry.grid(row=8, column=0)
    OKButton = ttk.Button(PopupFrame, text="OK", command=lambda: NameAndDestroy("blah"))
    PopupWindow.bind("<Return>", NameAndDestroy)
    StockpileNameEntry.focus()
    OKButton.grid(row=10, column=0, sticky="NSEW")
