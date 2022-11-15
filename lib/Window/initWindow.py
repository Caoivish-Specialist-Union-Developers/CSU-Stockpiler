from tkinter import ttk


def initWindow():
    s = ttk.Style()
    s.theme_use("alt")
    s.configure("EnabledButton.TButton", background="gray")
    s.configure("DisabledButton.TButton", background="red2")
    # Manually disabled button is different color because it is retained regardless of category/faction disable/enable
    s.configure("ManualDisabledButton.TButton", background="red4")
    s.configure("EnabledCategory.TButton", background="gray")
    s.configure("DisabledCategory.TButton", background="red2")
    s.configure("EnabledFaction.TButton", background="gray")
    s.configure("DisabledFaction.TButton", background="red2")
    s.configure(
        "TScrollbar",
        troughcolor="grey20",
        arrowcolor="grey20",
        background="gray",
        bordercolor="grey15",
    )
    s.configure("TFrame", background="black")
    s.configure("TCanvas", background="black")
    s.configure("TCheckbutton", background="black", foreground="grey75")
    s.configure("TWindow", background="black")
    s.map(
        "TCheckbutton",
        foreground=[
            ("!active", "grey75"),
            ("pressed", "black"),
            ("active", "black"),
            ("selected", "green"),
            ("alternate", "purple"),
        ],
        background=[
            ("!active", "black"),
            ("pressed", "grey75"),
            ("active", "white"),
            ("selected", "cyan"),
            ("alternate", "pink"),
        ],
        indicatorcolor=[("!active", "black"), ("pressed", "black"), ("selected", "grey75")],
        indicatorbackground=[
            ("!active", "green"),
            ("pressed", "pink"),
            ("selected", "red"),
        ],
    )
    s.configure("TNotebook", background="grey25", foreground="grey15", borderwidth=0)
    s.map(
        "TNotebook.Tab",
        foreground=[("active", "black"), ("selected", "black")],
        background=[("active", "grey80"), ("selected", "grey65")],
    )
    s.configure("TNotebook.Tab", background="grey40", foreground="black", borderwidth=0)
    s.configure(
        "TRadiobutton",
        background="black",
        indicatorbackground="blue",
        indicatorcolor="grey20",
        foreground="grey75",
        focuscolor="grey20",
    )
    s.map(
        "TRadiobutton",
        foreground=[
            ("!active", "grey75"),
            ("pressed", "black"),
            ("active", "black"),
            ("selected", "green"),
            ("alternate", "purple"),
        ],
        background=[
            ("!active", "black"),
            ("pressed", "grey15"),
            ("active", "white"),
            ("selected", "cyan"),
            ("alternate", "pink"),
        ],
    )
    s.configure("TLabel", background="black", foreground="grey75")