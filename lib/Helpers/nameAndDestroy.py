def NameAndDestroy(event):
    global PopupWindow
    global NewStockpileName
    global StockpileNameEntry
    NewStockpileName = StockpileNameEntry.get()
    PopupWindow.destroy()
