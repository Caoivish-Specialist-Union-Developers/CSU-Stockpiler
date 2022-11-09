from tkinter import Toplevel, ttk
from pynput.mouse import Button, Controller


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """


    def __init__(self, widget, text="widget info"):
        self.waittime = 100  # miliseconds before popup appear
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        mouse = Controller()
        current_mouse_position = mouse.position
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x, y = mouse.position
        # have popup slightly offset from mouse
        x += 15
        y += 15
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = ttk.Label(
            self.tw,
            text=self.text,
            justify="left",
            relief="ridge",
            borderwidth=5,
            background="grey25",
            foreground="white",
            wraplength=self.wraplength,
        )
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()
