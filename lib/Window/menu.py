from tkinter import *


def init():
    Version = "1.4b"

    StockpilerWindow = Tk()
    StockpilerWindow.title("Stockpiler " + Version)
    # Window width is based on generated UI.  If buttons change, width should change here.
    StockpilerWindow.geometry("537x600")
    # Width locked since button array doesn't adjust dynamically
    StockpilerWindow.resizable(width=False, height=False)
    StockpilerWindow.iconbitmap(default="Bmat.ico")

    class menu(object):
        iconrow = 1
        iconcolumn = 0
        lastcat = 0
        itembuttons = []
        icons = []
        category = [
            [0, 0],
            [1, 0],
            [2, 0],
            [3, 0],
            [4, 0],
            [5, 0],
            [6, 0],
            [7, 0],
            [8, 0],
            [9, 0],
        ]
        faction = [0, 0]
        topscroll = 0
        
        CSVExport = IntVar()

        # Update Discord Bot
        updateBot = IntVar() # Check Box for the setting
        BotHost = StringVar()
        BotPassword = StringVar()
        BotGuildID = StringVar()

        # Update API
        updateAPI = IntVar() # Checkbox for API update
        APIHost = StringVar() # Textbox for the host to send the results to
        APIKey = StringVar() # API key (optional)

        XLSXExport = IntVar()
        ImgExport = IntVar()
        debug = IntVar()
        Set = IntVar()
        Learning = IntVar()
        PickerX = -1
        PickerY = -1
        bindings = list()
        grabshift = IntVar()
        grabctrl = IntVar()
        grabalt = IntVar()
        grabhotkey = StringVar()
        scanshift = IntVar()
        scanctrl = IntVar()
        scanalt = IntVar()
        scanhotkey = StringVar()
        grabhotkeystring = "f2"
        scanhotkeystring = "f3"
        grabmods = "000"
        scanmods = "000"

    return menu, StockpilerWindow
