# Outside libraries import
import os
import os.path
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, ImageGrab, Image
import logging
import datetime
from pynput.mouse import Button, Controller
import glob
import cv2
import numpy as np
from global_hotkeys import *
import csv
import re
import xlsxwriter
from tksheet import Sheet
import requests
import threading

# Internal Packages Import
from logCleanup import logSetupCleanup
from lib.Window.menu import init
from lib.Window.initWindow import initWindow
from lib.Window.createToolTip import CreateToolTip
from lib.Requests.updateApi import updateApi

global stockpilename
global PopupWindow
global NewStockpileName
global StockpileNameEntry
global IconEntry
global IconName
global CurrentStockpileName
global IconPickerWindow
global IndOrCrateWindow
global FilterFrame
global LastStockpile
global tempicon


class items(object):
    data = []
    numbers = (
        ("CheckImages//num0.png", "0"),
        ("CheckImages//num1.png", "1"),
        ("CheckImages//num2.png", "2"),
        ("CheckImages//num3.png", "3"),
        ("CheckImages//num4.png", "4"),
        ("CheckImages//num5.png", "5"),
        ("CheckImages//num6.png", "6"),
        ("CheckImages//num7.png", "7"),
        ("CheckImages//num8.png", "8"),
        ("CheckImages//num9.png", "9"),
        ("CheckImages//numk.png", "k+"),
    )
    stockpilecontents = []
    sortedcontents = []
    slimcontents = []
    ThisStockpileName = ""
    FoundStockpileTypeName = ""
    UIimages = []


mouse = Controller()
current_mouse_position = mouse.position

# Logging

logSetupCleanup()

a = init()

StockpilerWindow = a[1]
menu = a[0]

menu.grabshift.set(0)
menu.grabctrl.set(0)
menu.grabalt.set(0)
menu.scanshift.set(0)
menu.scanctrl.set(0)
menu.scanalt.set(0)
menu.debug.set(0)

initWindow()


global hotkey
global listener
global vkclean
global vkorchar
global keyname
global justkey
global counter
global TargetDistanceEntry
global threadnum

counter = 1
threadnum = 1

filter = []

# Load contents of ItemNumbering.csv into items.data
# Adds all fields (columns) even though only a few are used
with open("ItemNumbering.csv", "rt") as f_input:
    csv_input = csv.reader(f_input, delimiter=",")
    # Skips first line
    header = next(csv_input)
    # Skips reserved line
    reserved = next(csv_input)
    for rowdata in csv_input:
        items.data.append(rowdata)
        if os.path.exists("UI//" + str(rowdata[0]) + ".png"):
            items.UIimages.append((rowdata[0], "UI//" + str(rowdata[0]) + ".png"))

# Load filter values into new array
with open("Filter.csv", "rt") as f_input:
    csv_input = csv.reader(f_input, delimiter=",")
    # Skips first line
    header = next(csv_input)
    for rowdata in csv_input:
        filter.append(rowdata)

# Matches up filter value with appropriate items in items.data
# for filteritem in range(len(filter)):
for item in range(len(items.data)):
    items.data[item].append(0)

for filteritem in range(len(filter)):
    # print(filter[filteritem])
    try:
        # print(filter[filteritem])
        for item in range(len(items.data)):
            if filter[filteritem][0] == items.data[item][0]:
                items.data[item][19] = filter[filteritem][1]
                # items.data[item].extend(filter[filteritem][1])
    except Exception as e:
        print("Exception: ", e)
        print("failed to apply filters to items.data")


print(items.data[1])


# For troubleshooting
# data[item].extend(filter[item][1])
# print(data)
# Names = [item[3] for item in data]
# print(Names)



# Function used simply for grabbing cropped stockpile images
# Helpful for grabbing test images for assembling missing icons or new sets of icons (for modded icons)
def GrabStockpileImage():
    global counter
    # OKAY, so you'll have to grab the whole screen, detect that thing in the upper left, then use that as a basis
    # for cropping that full screenshot down to just the foxhole window

    screen = np.array(
        ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=True)
    )
    greyscreen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

    numbox = cv2.imread("CheckImages//StateOf.png", cv2.IMREAD_GRAYSCALE)
    res = cv2.matchTemplate(greyscreen, numbox, cv2.TM_CCOEFF_NORMED)
    threshold = 0.95
    if np.amax(res) > threshold:
        stateloc = np.where(res >= threshold)
        print(stateloc)
        if stateloc[0].astype(int) - 35 >= 0:
            statey = stateloc[0].astype(int) - 35
        else:
            statey = 0
        if stateloc[1].astype(int) - 35 >= 0:
            statex = stateloc[1].astype(int) - 35
        else:
            statex = 0
        greyscreen = greyscreen[
            int(statey) : int(statey) + 1079, int(statex) : int(statex) + 1919
        ]
        if menu.debug.get() == 1:
            cv2.imshow("Grabbed in image GrabStockpileImage", screen)
            cv2.waitKey(0)
        if menu.Set.get() == 0:
            findshirtC = cv2.imread(
                "CheckImages//Default//86C.png", cv2.IMREAD_GRAYSCALE
            )
            findshirt = cv2.imread("CheckImages//Default//86.png", cv2.IMREAD_GRAYSCALE)
        else:
            findshirtC = cv2.imread(
                "CheckImages//Modded//86C.png", cv2.IMREAD_GRAYSCALE
            )
            findshirt = cv2.imread("CheckImages//Modded//86.png", cv2.IMREAD_GRAYSCALE)

        # Shirts are always in the same spot in every stockpile, but might be single or crates
        try:
            resC = cv2.matchTemplate(greyscreen, findshirtC, cv2.TM_CCOEFF_NORMED)
        except Exception as e:
            print("Exception: ", e)
            print("Maybe you don't have the shirt crate")
            logging.info(
                str(datetime.datetime.now())
                + " Exception loading shirt crate icon in GrabStockpileImage "
                + str(e)
            )
        try:
            res = cv2.matchTemplate(greyscreen, findshirt, cv2.TM_CCOEFF_NORMED)
        except Exception as e:
            print("Exception: ", e)
            print("Maybe you don't have the individual shirt")
            logging.info(
                str(datetime.datetime.now())
                + " Exception loading individual shirt icon in GrabStockpileImage "
                + str(e)
            )
        threshold = 0.99
        FoundShirt = False
        try:
            if np.amax(res) > threshold:
                print("Found Shirts")
                y, x = np.unravel_index(res.argmax(), res.shape)
                FoundShirt = True
        except Exception as e:
            print("Exception: ", e)
            print("Don't have the individual shirts icon or not looking at a stockpile")
            logging.info(
                str(datetime.datetime.now())
                + " Exception finding individual shirt icon in GrabStockpileImage "
                + str(e)
            )
        try:
            if np.amax(resC) > threshold:
                print("Found Shirt Crate")
                y, x = np.unravel_index(resC.argmax(), resC.shape)
                FoundShirt = True
        except Exception as e:
            print("Exception: ", e)
            print("Don't have the shirt crate icon or not looking at a stockpile")
            logging.info(
                str(datetime.datetime.now())
                + " Exception finding shirt crate icon in GrabStockpileImage "
                + str(e)
            )
        if not FoundShirt:
            print(
                "Found nothing.  Either don't have shirt icon(s) or not looking at a stockpile"
            )
            y = 0
            x = 0
        # If no stockpile was found, don't bother taking a screenshot, else crop based on where shirts were found
        if x == 0 and y == 0:
            print("Both 0's")
            pass
        else:
            stockpile = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
            stockpile = stockpile[
                int(y) - 32 : int(y) + 1080, int(x) - 11 : int(x) + 389
            ]
            imagename = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
            fullimagename = "test_" + imagename + ".png"
            cv2.imwrite(fullimagename, stockpile)
            logging.info(
                str(datetime.datetime.now())
                + " Saved image with GrabStockpileImage named "
                + fullimagename
            )
    else:
        print(
            "No State of the War detected in top left corner.  Either it is covered by something (Stockpiler maybe?)"
            " or the map is not open"
        )


def Learn(LearnInt, image):
    global counter
    global IconName
    global LastStockpile
    # grab whole screen and prepare for template matching
    # COMMENT OUT THESE TWO LINES IF YOU ARE TESTING A SPECIFIC IMAGE
    TestImage = False

    # WHEN USING OTHER RESOLUTIONS, GRAB THEM HERE
    resx = 1920
    resy = 1080

    try:
        # OKAY, so you'll have to grab the whole screen, detect that thing in the upper left, then use that as a basis
        # for cropping that full screenshot down to just the foxhole window
        screen = np.array(
            ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=True)
        )
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        numbox = cv2.imread("CheckImages//StateOf.png", cv2.IMREAD_GRAYSCALE)
        res = cv2.matchTemplate(screen, numbox, cv2.TM_CCOEFF_NORMED)
        threshold = 0.95
        if np.amax(res) > threshold:
            stateloc = np.where(res >= threshold)
            if stateloc[0].astype(int) - 35 >= 0:
                statey = stateloc[0].astype(int) - 35
            else:
                statey = 0
            if stateloc[1].astype(int) - 35 >= 0:
                statex = stateloc[1].astype(int) - 35
            else:
                statex = 0
            # If/when it moves to multiple resolutions, these hardcoded sizes will need to be variables
            screen = screen[
                int(statey) : int(statey) + resy, int(statex) : int(statex) + resx
            ]
            print(
                "It thinks it found the window position in Learn and is grabbing location: X:",
                str(statex),
                " Y:",
                str(statey),
            )
            if menu.debug.get() == 1:
                cv2.imshow("Grabbed in Learn, found State of War", screen)
                cv2.waitKey(0)
        else:
            print(
                "State of the War not found in Learn.  It may be covered up or you're not on the map."
            )
            if menu.debug.get() == 1:
                cv2.imshow("Grabbed in Learn, did NOT find State of War", screen)
                cv2.waitKey(0)
    except Exception as e:
        print("Exception: ", e)
        print("Failed to grab the screen in Learn")
        logging.info(
            str(datetime.datetime.now())
            + " Failed Grabbing the screen in Learn "
            + str(e)
        )

    # UNCOMMENT AND MODIFY LINE BELOW IF YOU ARE TESTING A SPECIFIC IMAGE
    # screen = cv2.cvtColor(np.array(Image.open("test_2021-11-25-110247.png")), cv2.COLOR_RGB2GRAY)
    # TestImage = True

    if LearnInt != "":
        pass
    else:
        screen = LastStockpile

    numbox = cv2.imread("CheckImages//NumBox.png", cv2.IMREAD_GRAYSCALE)
    res = cv2.matchTemplate(screen, numbox, cv2.TM_CCOEFF_NORMED)
    threshold = 0.99
    if np.amax(res) > threshold:
        numloc = np.where(res >= threshold)
        print("found them here:", numloc)
        print(len(numloc[0]))
        for spot in range(len(numloc[0])):
            # Stockpiles never displayed in upper left under State of the War area
            # State of the War area throws false positives for icons
            if (
                numloc[1][spot] < (resx * 0.2)
                and numloc[0][spot] < (resy * 0.24)
                and not TestImage
            ):
                pass
            else:
                print("x:", numloc[1][spot], " y:", numloc[0][spot])
                # cv2.imshow('icon', screen[int(numloc[0][spot]+2):int(numloc[0][spot]+36), int(numloc[1][spot]-38):numloc[1][spot]-4])
                # cv2.waitKey(0)
                currenticon = screen[
                    int(numloc[0][spot] + 2) : int(numloc[0][spot] + 36),
                    int(numloc[1][spot] - 38) : numloc[1][spot] - 4,
                ]
                print("currenticon:", currenticon.shape)
                if menu.Set.get() == 0:
                    folder = "CheckImages//Default//"
                else:
                    folder = "CheckImages//Modded//"
                Found = False
                for imagefile in os.listdir(folder):
                    checkimage = cv2.imread(folder + imagefile, cv2.IMREAD_GRAYSCALE)
                    print("Checking for ", str(imagefile))
                    result = cv2.matchTemplate(
                        currenticon, checkimage, cv2.TM_CCOEFF_NORMED
                    )
                    threshold = 0.99
                    if np.amax(result) > threshold:
                        # print("Found:", imagefile)
                        Found = True
                        break
                if not Found:
                    print("Not found, should launch IconPicker")
                    IconCatPicker(currenticon, 0)
                    # IconPicker(currenticon)
        SearchImage(1, screen)
        CreateButtons("blah")
    else:
        print("Found no numboxes, which is very strange")
        if menu.debug.get() == 1:
            cv2.imshow("No numboxes?", screen)
            cv2.waitKey(0)


def SearchImage(Pass, LearnImage):
    global stockpilename
    global NewStockpileName
    global PopupWindow
    global CurrentStockpileName
    global threadnum

    if Pass != "":
        screen = LearnImage
    else:
        try:
            # OKAY, so you'll have to grab the whole screen, detect that thing in the upper left, then use that as a basis
            # for cropping that full screenshot down to just the foxhole window
            screen = np.array(
                ImageGrab.grab(
                    bbox=None, include_layered_windows=False, all_screens=True
                )
            )
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

            numbox = cv2.imread("CheckImages//StateOf.png", cv2.IMREAD_GRAYSCALE)
            res = cv2.matchTemplate(screen, numbox, cv2.TM_CCOEFF_NORMED)
            threshold = 0.95
            if np.amax(res) > threshold:
                stateloc = np.where(res >= threshold)
                if stateloc[0].astype(int) - 35 >= 0:
                    statey = stateloc[0].astype(int) - 35
                else:
                    statey = 0
                if stateloc[1].astype(int) - 35 >= 0:
                    statex = stateloc[1].astype(int) - 35
                else:
                    statex = 0
                screen = screen[
                    int(statey) : int(statey) + 1079, int(statex) : int(statex) + 1919
                ]
                print(
                    "It thinks it found the window position in SearchImage and is grabbing location: X:",
                    str(statex),
                    " Y:",
                    str(statey),
                )
                if menu.debug.get() == 1:
                    cv2.imshow("Grabbed in SearchImage", screen)
                    cv2.waitKey(0)
            else:
                print(
                    "State of the War not found in SearchImage.  It may be covered up or you're not on the map."
                )
                if menu.debug.get() == 1:
                    cv2.imshow(
                        "Grabbed in SearchImage, did NOT find State of War", screen
                    )
                    cv2.waitKey(0)
        except Exception as e:
            print("Exception: ", e)
            print("Failed to grab the screen in SearchImage")
            logging.info(
                str(datetime.datetime.now())
                + " Failed Grabbing the screen in SearchImage "
                + str(e)
            )
    garbage = "blah"
    args = (screen, garbage)
    # Threading commands are generated via text since each thread needs a distinct name, created using threadcounter
    threadcounter = "t" + str(threadnum)
    # print(threadcounter)
    logging.info(
        str(datetime.datetime.now()) + " Starting scan thread: " + str(threadcounter)
    )
    threadingthread = (
        threadcounter + " = threading.Thread(target = ItemScan, args = args)"
    )
    threadingdaemon = threadcounter + ".daemon = True"
    threadingstart = threadcounter + ".start()"
    # print(threadnum)
    exec(threadingthread)
    exec(threadingdaemon)
    exec(threadingstart)
    threadnum += 1


def ItemScan(screen, garbage):
    global LastStockpile
    if menu.Set.get() == 0:
        findshirtC = cv2.imread("CheckImages//Default//86C.png", cv2.IMREAD_GRAYSCALE)
        findshirt = cv2.imread("CheckImages//Default//86.png", cv2.IMREAD_GRAYSCALE)
    else:
        try:
            findshirtC = cv2.imread(
                "CheckImages//Modded//86C.png", cv2.IMREAD_GRAYSCALE
            )
        except Exception as e:
            print("Exception: ", e)
            print("You don't have the Shirt crate yet in ItemScan")
            logging.info(
                str(datetime.datetime.now())
                + " Failed loading modded shirt crate icon in ItemScan "
                + str(e)
            )
        try:
            findshirt = cv2.imread("CheckImages//Modded//86.png", cv2.IMREAD_GRAYSCALE)
        except Exception as e:
            print("Exception: ", e)
            print("You don't have the individual Shirt yet in ItemScan")
            logging.info(
                str(datetime.datetime.now())
                + " Failed loading modded individual shirt icon in ItemScan "
                + str(e)
            )
    try:
        resC = cv2.matchTemplate(screen, findshirtC, cv2.TM_CCOEFF_NORMED)
    except Exception as e:
        print("Exception: ", e)
        print("Looks like you're missing the shirt crate in ItemScan")
        logging.info(
            str(datetime.datetime.now())
            + " Maybe missing shirt crate icon in ItemScan "
            + str(e)
        )
    try:
        res = cv2.matchTemplate(screen, findshirt, cv2.TM_CCOEFF_NORMED)
    except Exception as e:
        print("Exception: ", e)
        print("Looks like you're missing the individual shirts in ItemScan")
        logging.info(
            str(datetime.datetime.now())
            + " Maybe missing individual shirt icon in ItemScan "
            + str(e)
        )
    threshold = 0.99
    FoundShirt = False
    try:
        if np.amax(res) > threshold:
            print("Found Shirts")
            y, x = np.unravel_index(res.argmax(), res.shape)
            FoundShirt = True
    except Exception as e:
        print("Exception: ", e)
        print(
            "Don't have the individual shirts icon or not looking at a stockpile in ItemScan"
        )
        logging.info(
            str(datetime.datetime.now())
            + " Don't have the individual shirts icon or not looking at a stockpile in ItemScan "
            + str(e)
        )
    try:
        if np.amax(resC) > threshold:
            print("Found Shirt Crate")
            y, x = np.unravel_index(resC.argmax(), resC.shape)
            FoundShirt = True
    except Exception as e:
        print("Exception: ", e)
        print(
            "Don't have the shirt crate icon or not looking at a stockpile in ItemScan"
        )
        logging.info(
            str(datetime.datetime.now())
            + " Don't have the shirt crate icon or not looking at a stockpile in ItemScan "
            + str(e)
        )
    if not FoundShirt:
        print(
            "Found nothing.  Either don't have shirt icon(s) or not looking at a stockpile in ItemScan"
        )
        y = 0
        x = 0

    # COMMENT OUT IF TESTING A SPECIFIC IMAGE
    if y == x == 0:
        stockpile = screen
    else:
        stockpile = screen[y - 32 : 1080, x - 11 : x + 389]

    if menu.debug.get() == 1:
        cv2.imshow("Stockpile in this image in ItemScan?", stockpile)
        cv2.waitKey(0)
    # UNCOMMENT IF TESTING A SPECIFIC IMAGE
    # stockpile = screen

    # Grab this just in case you need to rerun the scan from Results tab
    # LastStockpile = stockpile
    LastStockpile = screen

    # Image clips for each type of stockpile should be in this array below
    StockpileTypes = (
        ("CheckImages//Seaport.png", "Seaport", 0),
        ("Checkimages//StorageDepot.png", "Storage Depot", 1),
        ("Checkimages//Outpost.png", "Outpost", 2),
        ("Checkimages//Townbase.png", "Town Base", 3),
        ("Checkimages//RelicBase.png", "Relic Base", 4),
        ("Checkimages//BunkerBase.png", "Bunker Base", 5),
        ("Checkimages//Encampment.png", "Encampment", 6),
        ("Checkimages//SafeHouse.png", "Safe House", 7),
    )
    # Check cropped stockpile image for each location type image
    for image in StockpileTypes:
        try:
            findtype = cv2.imread(image[0], cv2.IMREAD_GRAYSCALE)
            if menu.debug.get() == 1:
                cv2.imshow("Looking for this", findtype)
                cv2.waitKey(0)
            res = cv2.matchTemplate(stockpile, findtype, cv2.TM_CCOEFF_NORMED)
            # Threshold is a bit lower for types as they are slightly see-thru
            typethreshold = 0.95
            # print("Checking:", image[1])
            if np.amax(res) > typethreshold:
                y, x = np.unravel_index(res.argmax(), res.shape)
                FoundStockpileType = image[2]
                FoundStockpileTypeName = image[1]
                # print(image[1])
                if image[1] == "Seaport" or image[1] == "Storage Depot":
                    findtab = cv2.imread("CheckImages//Tab.png", cv2.IMREAD_GRAYSCALE)
                    res = cv2.matchTemplate(stockpile, findtab, cv2.TM_CCOEFF_NORMED)
                    tabthreshold = 0.95
                    if np.amax(res) > tabthreshold:
                        print("Found the Tab")
                        y, x = np.unravel_index(res.argmax(), res.shape)
                        # Seaports and Storage Depots have the potential to have named stockpiles, so grab the name
                        stockpilename = stockpile[y - 5 : y + 17, x - 150 : x - 8]
                        # Make a list of all current stockpile name images
                        currentstockpiles = glob.glob("Stockpiles/*.png")
                        # print(currentstockpiles)
                        found = 0
                        for image in currentstockpiles:
                            stockpilelabel = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
                            if not image.endswith("image.png"):
                                res = cv2.matchTemplate(
                                    stockpilename, stockpilelabel, cv2.TM_CCOEFF_NORMED
                                )
                                threshold = 0.99
                                flag = False
                                if np.amax(res) > threshold:
                                    # Named stockpile is one already seen
                                    found = 1
                                    ThisStockpileName = image[11 : (len(image) - 4)]
                        if found != 1:
                            newstockpopup(stockpilename)
                            PopupWindow.wait_window()
                            if (
                                NewStockpileName == ""
                                or NewStockpileName.lower() == "public"
                            ):
                                popup("BlankName")
                                ThisStockpileName = "TheyLeftTheStockpileNameBlank"
                            else:
                                # NewStockpileFilename = 'Stockpiles//' + NewStockpileName + '.png'
                                # It's a new stockpile, so save an images of the name as well as the cropped stockpile itself
                                cv2.imwrite(
                                    "Stockpiles//" + NewStockpileName + ".png",
                                    stockpilename,
                                )
                                if menu.ImgExport.get() == 1:
                                    cv2.imwrite(
                                        "Stockpiles//"
                                        + NewStockpileName
                                        + " image.png",
                                        stockpile,
                                    )
                                ThisStockpileName = NewStockpileName
                    else:
                        # It's not a named stockpile, so just call it by the type of location (Bunker Base, Encampment, etc)
                        print(
                            "Didn't find the Tab, so it looks like it's not a named stockpile"
                        )
                        ThisStockpileName = FoundStockpileTypeName
                else:
                    # It's not a named stockpile, so just call it by the type of location (Bunker Base, Encampment, etc)
                    print(
                        "Not a named stockpile, it's a Bunker Base, Encampment, something like that"
                    )
                    ThisStockpileName = FoundStockpileTypeName
                # StockpileName = StockpileNameEntry.get()
                # cv2.imwrite('Stockpiles//' + StockpileName + '.png', stockpilename)
                break
            else:
                # print("Didn't find",image[1])
                print("Doesn't look like any known stockpile type")
                FoundStockpileType = "None"
                ThisStockpileName = "None"
                pass
        except Exception as e:
            print("Exception: ", e)
            print(
                "Probably not looking at a stockpile or don't have the game open.  Looked for: ",
                str(image),
            )
            FoundStockpileType = "None"
            ThisStockpileName = "None"
            logging.info(
                str(datetime.datetime.now())
                + " Probably not looking at a stockpile or don't have the game open."
            )
            logging.info(
                str(datetime.datetime.now()) + " Looked for: ", str(image) + str(e)
            )
            pass

    # These stockpile types allow for crates (ie: Seaport)
    CrateList = [0, 1]
    # These stockpile types only allow individual items (ie: Bunker Base)
    SingleList = [2, 3, 4, 5, 6, 7]

    start = datetime.datetime.now()

    print(ThisStockpileName)
    if ThisStockpileName == "TheyLeftTheStockpileNameBlank":
        pass
    else:
        if menu.Set.get() == 0:
            folder = "CheckImages//Default//"
        else:
            folder = "CheckImages//Modded//"
        if ThisStockpileName != "None":
            if menu.ImgExport.get() == 1:
                cv2.imwrite(
                    "Stockpiles//" + ThisStockpileName + " image.png", stockpile
                )
            if FoundStockpileType in CrateList:
                print("Crate Type")
                # Grab all the crate CheckImages
                print(item)
                StockpileImages = [
                    (
                        str(item[0]),
                        folder + str(item[0]) + "C.png",
                        (item[3] + " Crate"),
                        item[8],
                        item[12],
                    )
                    for item in items.data
                    if str(item[19]) == "0"
                ]
                # Grab all the individual vehicles and shippables
                StockpileImagesAppend = [
                    (
                        str(item[0]),
                        folder + str(item[0]) + ".png",
                        item[3],
                        item[8],
                        item[11],
                    )
                    for item in items.data
                    if (str(item[9]) == "7" and str(item[19]) == "0")
                    or (str(item[9]) == "8" and str(item[19]) == "0")
                ]
                StockpileImages.extend(StockpileImagesAppend)
                # print("Checking for:", StockpileImages)
            elif FoundStockpileType in SingleList:
                print("Single Type")
                # Grab all the individual items
                # for item in range(len(items.data)):
                # 	print(item)
                StockpileImages = [
                    (
                        str(item[0]),
                        folder + str(item[0]) + ".png",
                        item[3],
                        item[8],
                        item[11],
                    )
                    for item in items.data
                ]
                # print("Checking for:", StockpileImages)
            else:
                print("No idea what type...")

            stockpilecontents = []
            checked = 0
            # print("StockpileImages", StockpileImages)
            for image in StockpileImages:
                checked += 1
                if str(image[4]) == "1":
                    if os.path.exists(image[1]):
                        try:
                            findimage = cv2.imread(image[1], cv2.IMREAD_GRAYSCALE)
                            res = cv2.matchTemplate(
                                stockpile, findimage, cv2.TM_CCOEFF_NORMED
                            )
                            threshold = 0.99
                            flag = False
                            if np.amax(res) > threshold:
                                flag = True
                                y, x = np.unravel_index(res.argmax(), res.shape)
                                # Found a thing, now find amount
                                numberlist = []
                                for number in items.numbers:
                                    findnum = cv2.imread(
                                        number[0], cv2.IMREAD_GRAYSCALE
                                    )
                                    # Clip the area where the stock number will be
                                    numberarea = stockpile[
                                        y + 8 : y + 28, x + 45 : x + 87
                                    ]
                                    resnum = cv2.matchTemplate(
                                        numberarea, findnum, cv2.TM_CCOEFF_NORMED
                                    )
                                    threshold = 0.90
                                    numloc = np.where(resnum >= threshold)
                                    # It only looks for up to 3 of each number for each item, since after that it would be a "k+" scenario, which never happens in stockpiles
                                    # This will need to be changed to allow for more digits whenever it does in-person looks at BB stockpiles and such, where it will show up to 5 digits
                                    if len(numloc[1]) > 0:
                                        numberlist.append(
                                            tuple([numloc[1][0], number[1]])
                                        )
                                    if len(numloc[1]) > 1:
                                        numberlist.append(
                                            tuple([numloc[1][1], number[1]])
                                        )
                                    if len(numloc[1]) > 2:
                                        numberlist.append(
                                            tuple([numloc[1][2], number[1]])
                                        )
                                    # Sort the list of numbers by position closest to the left, putting the numbers in order by extension
                                    numberlist.sort(key=lambda y: y[0])

                                # If the number ends in a K, it just adds 000 since you don't know if that's 1001 or 1999
                                # k+ never happens in stockpiles, so this only affects town halls, bunker bases, etc
                                if len(numberlist) == 1:
                                    quantity = int(str(numberlist[0][1]))
                                elif len(numberlist) == 2:
                                    if numberlist[1][1] == "k+":
                                        quantity = int(str(numberlist[0][1]) + "000")
                                    else:
                                        quantity = int(
                                            str(numberlist[0][1])
                                            + (str(numberlist[1][1]))
                                        )
                                elif len(numberlist) == 3:
                                    if numberlist[2][1] == "k+":
                                        quantity = int(
                                            str(numberlist[0][1])
                                            + (str(numberlist[1][1]))
                                            + "000"
                                        )
                                    else:
                                        quantity = int(
                                            str(numberlist[0][1])
                                            + (str(numberlist[1][1]))
                                            + str(numberlist[2][1])
                                        )
                                elif len(numberlist) == 4:
                                    if numberlist[3][1] == "k+":
                                        quantity = int(
                                            str(numberlist[0][1])
                                            + (str(numberlist[1][1]))
                                            + str(numberlist[2][1])
                                            + "000"
                                        )
                                    else:
                                        quantity = int(
                                            str(numberlist[0][1])
                                            + (str(numberlist[1][1]))
                                            + str(numberlist[2][1])
                                            + str(numberlist[3][1])
                                        )
                                # place shirts first, since they're always at the top of every stockpile
                                if image[0] == "86":
                                    itemsort = 0
                                # bunker supplies next
                                elif image[0] == "93":
                                    itemsort = 1
                                # garrison supplies last
                                elif image[0] == "90":
                                    itemsort = 2
                                elif image[3] != "Vehicle" and image[3] != "Shippables":
                                    itemsort = 5
                                elif image[3] == "Vehicle":
                                    itemsort = 10
                                else:
                                    itemsort = 15
                                if (
                                    image[1][(len(image[1]) - 5) : (len(image[1]) - 4)]
                                    == "C"
                                ):
                                    stockpilecontents.append(
                                        list(
                                            (image[0], image[2], quantity, itemsort, 1)
                                        )
                                    )
                                else:
                                    stockpilecontents.append(
                                        list(
                                            (image[0], image[2], quantity, itemsort, 0)
                                        )
                                    )
                        except Exception as e:
                            print("Exception: ", e)
                            if menu.debug.get() == 1:
                                print("Failed while looking for: ", str(image[2]))
                                logging.info(
                                    str(datetime.datetime.now())
                                    + "Failed while looking for (missing?): ",
                                    str(image[2]) + str(e),
                                )
                            pass
                    else:
                        if menu.debug.get() == 1:
                            print("File missing:", str(image[1]), str(image[2]))
                else:
                    if menu.debug.get() == 1:
                        print(
                            "Skipping icon: ",
                            str(image[2]),
                            "because ItemNumbering.csv lists it as impossible/never displayed in stockpile images (like pistol ammo and crates of warheads)",
                            image[4],
                        )
                    pass

            items.sortedcontents = list(
                sorted(stockpilecontents, key=lambda x: (x[3], x[4], -x[2]))
            )
            # Here's where we sort stockpilecontents by category, then number, so they spit out the same as screenshot
            # Everything but vehicles and shippables first, then single vehicle, then crates of vehicles, then single shippables, then crates of shippables
            if ThisStockpileName in (
                "Seaport",
                "Storage Depot",
                "Outpost",
                "Town Base",
                "Relic Base",
                "Bunker Base",
                "Encampment",
                "Safe House",
            ):
                ThisStockpileName = "Public"

            if menu.CSVExport.get() == 1:
                stockpilefile = open("Stockpiles//" + ThisStockpileName + ".csv", "w")
                stockpilefile.write(ThisStockpileName + ",\n")
                stockpilefile.write(FoundStockpileTypeName + ",\n")
                stockpilefile.write(
                    str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ",\n"
                )
                stockpilefile.close()

                # Writing to both csv and xlsx, only the quantity and name is written
                # If more elements from items.data are added to stockpilecontents, they could be added to these exports as fields
                with open("Stockpiles//" + ThisStockpileName + ".csv", "a") as fp:
                    # fp.write('\n'.join('{},{},{}'.format(x[0],x[1],x[2]) for x in stockpilecontents))
                    ############### THIS ONE DOES IN REGULAR ORDER ############
                    # fp.write('\n'.join('{},{}'.format(x[1],x[2]) for x in stockpilecontents))
                    ############### THIS ONE DOES IN SORTED ORDER #############
                    fp.write(
                        "\n".join(
                            "{},{}".format(x[1], x[2]) for x in items.sortedcontents
                        )
                    )
                fp.close()

            # Update the CSU API

            updateApi(menu, items, ThisStockpileName)

            if menu.XLSXExport.get() == 1:
                workbook = xlsxwriter.Workbook(
                    "Stockpiles//" + ThisStockpileName + ".xlsx"
                )
                worksheet = workbook.add_worksheet()
                worksheet.write(0, 0, ThisStockpileName)
                worksheet.write(1, 0, FoundStockpileTypeName)
                worksheet.write(
                    2, 0, str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                row = 3
                for col, data in enumerate(items.sortedcontents):
                    # print("col", col, " data", data)
                    worksheet.write(row + col, 0, data[1])
                    worksheet.write(row + col, 1, data[2])
                workbook.close()
            print(datetime.datetime.now() - start)
            print("Items Checked:", checked)
            items.slimcontents = items.sortedcontents
            for sublist in items.slimcontents:
                del sublist[3:5]
            ResultSheet.set_sheet_data(data=items.slimcontents)
        else:
            popup("NoStockpile")


def LearnOrNot():
    if menu.Learning.get() == 0:
        SearchImage("", "")
    else:
        Learn(0, "img")


def newstockpopup(image):
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


def popup(type):
    global PopupWindow
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
    if type == "NoFox":
        NoFoxholeLabel = ttk.Label(
            PopupFrame,
            text="Foxhole isn't running.\nLaunch Foxhole and retry.",
            style="TLabel",
        )
        NoFoxholeLabel.grid(row=2, column=0)
    elif type == "NoStockpile":
        NoStockpileLabel = ttk.Label(
            PopupFrame,
            text="Didn't detect stockpile.\nHover over a stockpile on the map and "
            "retry.",
            style="TLabel",
        )
        NoStockpileLabel.grid(row=2, column=0)
    elif type == "BlankName":
        BlankorPublicLabel = ttk.Label(
            PopupFrame,
            text="You must type in the name (which cannot be Public).\nThis field "
            "cannot be left blank.\nYou'll need to rescan it.",
            style="TLabel",
        )
        BlankorPublicLabel.grid(row=2, column=0)
    elif type == "DuplicateHotkeys":
        DuplicateHotkeyLabel = ttk.Label(
            PopupFrame,
            text="Warning: If your hotkeys are identical or overlap (ie: F2 and"
            " Shift + F2)\nthen it's possible that the hotkey will only "
            "grab a stockpile image and will not scan.",
        )
        DuplicateHotkeyLabel.grid(row=2, column=0)
    OKButton = ttk.Button(PopupFrame, text="OK", command=lambda: Destroy("blah"))
    PopupWindow.bind("<Return>", Destroy)
    OKButton.grid(row=10, column=0, sticky="NSEW")


def NameAndDestroy(event):
    global PopupWindow
    global NewStockpileName
    global StockpileNameEntry
    NewStockpileName = StockpileNameEntry.get()
    PopupWindow.destroy()


def SaveIconAndDestroy(image):
    global PopupWindow
    global IconEntry
    global IconName
    IconName = IconEntry.get()
    if IconName != "":
        if menu.Set.get() == 0:
            folder = "CheckImages//Default//"
        else:
            folder = "CheckImages//Modded//"
        cv2.imwrite(folder + IconName + ".png", image)
    PopupWindow.destroy()


def CancelIcon(event):
    global PopupWindow


def Destroy(event):
    global PopupWindow
    PopupWindow.destroy()


def CSVExport():
    if items.stockpilecontents != []:
        stockpilefile = open("Stockpiles//" + items.ThisStockpileName + ".csv", "w")
        stockpilefile.write(items.ThisStockpileName + ",\n")
        stockpilefile.write(items.FoundStockpileTypeName + ",\n")
        stockpilefile.write(
            str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ",\n"
        )
        stockpilefile.close()

        # Writing to both csv and xlsx, only the quantity and name is written
        # If more elements from items.data are added to stockpilecontents, they could be added to these exports as fields
        with open("Stockpiles//" + items.ThisStockpileName + ".csv", "a") as fp:
            # fp.write('\n'.join('{},{},{}'.format(x[0],x[1],x[2]) for x in stockpilecontents))
            ############### THIS ONE DOES IN REGULAR ORDER ############
            # fp.write('\n'.join('{},{}'.format(x[1],x[2]) for x in stockpilecontents))
            ############### THIS ONE DOES IN SORTED ORDER #############
            fp.write(
                "\n".join("{},{}".format(x[1], x[2]) for x in items.sortedcontents)
            )
        fp.close()


def XLSXExport():
    if items.stockpilecontents != []:
        workbook = xlsxwriter.Workbook(
            "Stockpiles//" + items.ThisStockpileName + ".xlsx"
        )
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, items.ThisStockpileName)
        worksheet.write(1, 0, items.FoundStockpileTypeName)
        worksheet.write(
            2, 0, str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        row = 3
        for col, data in enumerate(items.sortedcontents):
            # print("col", col, " data", data)
            worksheet.write(row + col, 0, data[1])
            worksheet.write(row + col, 1, data[2])
        workbook.close()


def _on_mousewheel(event):
    FilterCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


OuterFrame = ttk.Frame(StockpilerWindow)
OuterFrame.pack(fill=BOTH, expand=1)
TabControl = ttk.Notebook(OuterFrame)
FilterTab = ttk.Frame(TabControl)
TabControl.add(FilterTab, text="Filter")
TableTab = ttk.Frame(TabControl)
TabControl.add(TableTab, text="Results")
SettingsTab = ttk.Frame(TabControl)
TabControl.add(SettingsTab, text="Settings")
TabControl.pack(expand=1, fill=BOTH)

FilterCanvas = Canvas(FilterTab)
TableCanvas = Canvas(TableTab)
SettingsCanvas = Canvas(SettingsTab)

FilterCanvas.bind_all("<MouseWheel>", _on_mousewheel)
scrollbar = ttk.Scrollbar(FilterTab, orient=VERTICAL, command=FilterCanvas.yview)
scrollbar.pack(side="right", fill="y")
# StockpileFrame = ttk.Frame(FilterCanvas, style="TFrame")

FilterCanvas.configure(
    scrollregion=FilterCanvas.bbox("all"), yscrollcommand=scrollbar.set
)
FilterCanvas.bind(
    "<Configure>",
    lambda e: FilterCanvas.configure(scrollregion=FilterCanvas.bbox("all")),
)


# If enough items are added, then the height below will have to be modified to account for any new button rows
# Remember to make sure the Quit button is displayed


FilterCanvas.pack(side=LEFT, fill=BOTH, expand=1)
TableCanvas.pack(side=TOP, fill=BOTH, expand=1)
SettingsCanvas.pack(side=TOP, fill=BOTH, expand=1)

FilterFrame = ttk.Frame(FilterCanvas)
TableFrame = ttk.Frame(TableCanvas)
SettingsFrame = ttk.Frame(SettingsCanvas)

# create_window height for Filter canvas should be roughly: is below
FilterCanvas.create_window(
    (0, 0), window=FilterFrame, anchor="nw", height="2024p", width="550p"
)
TableCanvas.create_window(
    (0, 0), window=TableFrame, anchor="nw", height="410p", width="402p"
)
SettingsCanvas.create_window(
    (0, 0), window=SettingsFrame, anchor="nw", height="500p", width="402p"
)

FilterFrame.bind(
    "<Configure>",
    lambda e: FilterCanvas.configure(scrollregion=FilterCanvas.bbox("all")),
)

fillerdata = 0
TableBottom = ttk.Frame(TableCanvas)
TableBottom.columnconfigure(0, weight=1)
TableBottom.columnconfigure(1, weight=1)
TableBottom.columnconfigure(2, weight=1)

TableBottom.pack(fill="x", side=BOTTOM)

ResultSheet = Sheet(TableFrame, data=fillerdata)
ResultSheet.enable_bindings()
ResultSheet.pack(expand=True, fill="both")
ResultSheet.set_options(
    table_bg="grey75",
    header_bg="grey55",
    index_bg="grey55",
    top_left_bg="grey15",
    frame_bg="grey15",
)


def SaveFilter():
    os.remove("Filter.csv")
    with open("Filter.csv", "w") as filterfile:
        filterfile.write("Number,Filter\n")
        for line in range(len(items.data)):
            try:
                filterfile.write(
                    str(items.data[line][0]) + "," + str(items.data[line][19]) + "\n"
                )
            except Exception as e:
                print("Exception: ", e)
                logging.info(
                    str(datetime.datetime.now())
                    + " Failed loading filter on line: "
                    + str(line),
                    str(e),
                )
                print("Fail", line)

    with open("Config.txt", "w") as exportfile:
        exportfile.write(str(menu.CSVExport.get()) + "\n")
        exportfile.write(str(menu.XLSXExport.get()) + "\n")
        exportfile.write(str(menu.ImgExport.get()) + "\n")
        exportfile.write(str(menu.Set.get()) + "\n")
        exportfile.write(str(menu.Learning.get()) + "\n")
        exportfile.write(str(menu.updateAPI.get()) + "\n")
        exportfile.write(str(menu.APIHost.get()) + "\n")
        exportfile.write(str(menu.APIKey.get()) + "\n")
        exportfile.write(str(menu.grabhotkey.get()) + "\n")
        exportfile.write(str(menu.scanhotkey.get()) + "\n")
        menu.grabhotkeystring = menu.grabhotkey.get()
        menu.scanhotkeystring = menu.scanhotkey.get()
        exportfile.write(
            str(menu.grabshift.get())
            + str(menu.grabctrl.get())
            + str(menu.grabalt.get())
            + "\n"
        )
        exportfile.write(
            str(menu.scanshift.get())
            + str(menu.scanctrl.get())
            + str(menu.scanalt.get())
            + "\n"
        )
    menu.grabmods = (
        str(menu.grabshift.get()) + str(menu.grabctrl.get()) + str(menu.grabalt.get())
    )
    menu.scanmods = (
        str(menu.scanshift.get()) + str(menu.scanctrl.get()) + str(menu.scanalt.get())
    )
    SetHotkeys("")
    CreateButtons("")


def CreateButtons(self):
    global FilterFrame

    for widgets in FilterFrame.winfo_children():
        widgets.destroy()
    menu.iconrow = 1
    menu.iconcolumn = 0
    menu.lastcat = 0
    menu.itembuttons = []
    menu.icons = []
    sortedicons = []
    counter = 0
    if menu.Set.get() == 0:
        folder = "CheckImages//Default//"
    else:
        folder = "CheckImages//Modded//"
    for i in range(len(items.data) + 1):
        for x in items.data:
            if x[0] == str(i):
                if os.path.exists(folder + str(i) + ".png") or os.path.exists(
                    folder + str(i) + "C.png"
                ):
                    try:
                        menu.icons.append(
                            (
                                i,
                                folder + str(i) + ".png",
                                int(x[9]),
                                int(x[10]),
                                int(x[19]),
                                str(x[3]),
                                str(x[8]),
                            )
                        )
                    except Exception as e:
                        print("Exception: ", e)
                        print(x[17])
                        print("oops", i)

    sortedicons = sorted(menu.icons, key=lambda x: (x[2], x[3]))

    SettingsFrame.columnconfigure(0, weight=1)
    SettingsFrame.columnconfigure(7, weight=1)
    GrabImageEntryLabel = ttk.Label(SettingsFrame, text="Grab Stockpile Image:")
    GrabImageEntryLabel.grid(row=menu.iconrow, column=0)
    GrabImageEntry = ttk.Entry(SettingsFrame, textvariable=menu.grabhotkey, width=10)
    GrabImageEntry.grid(row=menu.iconrow, column=1)
    GrabImageEntry.delete(0, "end")
    GrabImageEntry.insert(0, menu.grabhotkeystring)
    GrabImageEntry_ttp = CreateToolTip(
        GrabImageEntry,
        "Available hotkeys are: all letters, numbers, function keys (as f#)"
        ", backspace, tab, clear, enter, pause, caps_lock, escape, space, "
        "page_up, page_down, end, home, up, down, left, right, select, print, "
        "print_screen, insert, delete, help, numpad numbers (as numpad_#), "
        "separator_key (pipe key), multiply_key, add_key, subtract_key, "
        "decimal_key, divide_key, num_lock, scroll_lock, and symbols "
        "(+ - ` , . / ; [ ] ')",
    )
    GrabShiftCheck = ttk.Checkbutton(
        SettingsFrame, text="Shift?", variable=menu.grabshift
    )
    GrabShiftCheck.grid(row=menu.iconrow, column=2)
    GrabCtrlCheck = ttk.Checkbutton(SettingsFrame, text="Ctrl?", variable=menu.grabctrl)
    GrabCtrlCheck.grid(row=menu.iconrow, column=3)
    GrabAltCheck = ttk.Checkbutton(SettingsFrame, text="Alt?", variable=menu.grabalt)
    GrabAltCheck.grid(row=menu.iconrow, column=4)
    # LearningCheck = ttk.Checkbutton(SettingsFrame, text="Learning Mode?", variable=menu.Learning)

    menu.iconrow += 1
    ScanEntryLabel = ttk.Label(SettingsFrame, text="Scan Stockpile:")
    ScanEntryLabel.grid(row=menu.iconrow, column=0)
    ScanEntry = ttk.Entry(SettingsFrame, textvariable=menu.scanhotkey, width=10)
    ScanEntry.grid(row=menu.iconrow, column=1)
    ScanEntry.delete(0, "end")
    ScanEntry.insert(0, menu.scanhotkeystring)
    ScanEntry_ttp = CreateToolTip(
        ScanEntry,
        "Available hotkeys are: all letters, numbers, function keys (as f#)"
        ", backspace, tab, clear, enter, pause, caps_lock, escape, space, "
        "page_up, page_down, end, home, up, down, left, right, select, print, "
        "print_screen, insert, delete, help, numpad numbers (as numpad_#), "
        "separator_key (pipe key), multiply_key, add_key, subtract_key, "
        "decimal_key, divide_key, num_lock, scroll_lock, and symbols "
        "(+ - ` , . / ; [ ] ')",
    )
    ScanShiftCheck = ttk.Checkbutton(
        SettingsFrame, text="Shift?", variable=menu.scanshift
    )
    ScanShiftCheck.grid(row=menu.iconrow, column=2)
    ScanCtrlCheck = ttk.Checkbutton(SettingsFrame, text="Ctrl?", variable=menu.scanctrl)
    ScanCtrlCheck.grid(row=menu.iconrow, column=3)
    ScanAltCheck = ttk.Checkbutton(SettingsFrame, text="Alt?", variable=menu.scanalt)
    ScanAltCheck.grid(row=menu.iconrow, column=4)
    menu.iconrow += 1
    ResetHotkeysButton = ttk.Button(
        SettingsFrame, text="Reset Hotkeys", command=ResetHotkeys
    )
    ResetHotkeysButton.grid(row=menu.iconrow, column=0, columnspan=8, pady=1)
    ResetHotkeys_ttp = CreateToolTip(
        ResetHotkeysButton,
        "Some combinations may not work, like Ctrl + Shift + F-keys.\n"
        "This button will reset the hotkeys to default.  Remember to "
        "save your settings.",
    )
    menu.iconrow += 1
    setsep = ttk.Separator(SettingsFrame, orient=HORIZONTAL)
    setsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
    menu.iconrow += 1
    SetLabel = ttk.Label(SettingsFrame, text="Icon set?", style="TLabel")
    SetLabel.grid(row=menu.iconrow, column=0)
    DefaultRadio = ttk.Radiobutton(
        SettingsFrame, text="Default", variable=menu.Set, value=0
    )
    DefaultRadio.grid(row=menu.iconrow, column=1)
    ModdedRadio = ttk.Radiobutton(
        SettingsFrame, text="Modded", variable=menu.Set, value=1
    )
    ModdedRadio.grid(row=menu.iconrow, column=2)
    menu.iconrow += 1
    catsep = ttk.Separator(SettingsFrame, orient=HORIZONTAL)
    catsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
    menu.iconrow += 1
    LearningCheck = ttk.Checkbutton(
        SettingsFrame, text="Learning Mode?", variable=menu.Learning
    )
    LearningCheck.grid(row=menu.iconrow, column=0, columnspan=2)
    menu.iconrow += 1
    catsep = ttk.Separator(SettingsFrame, orient=HORIZONTAL)
    catsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
    menu.iconrow += 1
    CSVCheck = ttk.Checkbutton(SettingsFrame, text="CSV?", variable=menu.CSVExport)
    CSVCheck.grid(row=menu.iconrow, column=0)
    XLSXCheck = ttk.Checkbutton(SettingsFrame, text="XLSX?", variable=menu.XLSXExport)
    XLSXCheck.grid(row=menu.iconrow, column=1)
    ImgCheck = ttk.Checkbutton(SettingsFrame, text="Image?", variable=menu.ImgExport)
    ImgCheck.grid(row=menu.iconrow, column=2)
   

    # API update Settings
    menu.iconrow += 1
    catsep = ttk.Separator(SettingsFrame, orient=HORIZONTAL)
    catsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
    menu.iconrow += 1
    SendBotCheck = ttk.Checkbutton(
        SettingsFrame, text="Send to CSU API?", variable=menu.updateAPI
    )
    SendBotCheck.grid(row=menu.iconrow, column=0, rowspan=2, padx=5)
    SendBotCheck_ttp = CreateToolTip(
        SendBotCheck, "Send results to the CSU-Hub API to help log logi?"
    )
    BotHostLabel = ttk.Label(SettingsFrame, text="API Host:")
    BotHostLabel.grid(row=menu.iconrow, column=2)
    BotHost = ttk.Entry(SettingsFrame, textvariable=menu.APIHost)
    BotHost.grid(row=menu.iconrow, column=3, columnspan=2)
    BotHost_ttp = CreateToolTip(
        BotHost, "Host is found on the CSU Hub website under CHANGE ME"
    )
    menu.iconrow += 1
    BotPasswordLabel = ttk.Label(SettingsFrame, text="API Key:")
    BotPasswordLabel.grid(row=menu.iconrow, column=2)
    BotPassword = ttk.Entry(SettingsFrame, textvariable=menu.APIKey)
    BotPassword.grid(row=menu.iconrow, column=3, columnspan=2)
    BotPassword.config(show="*")
    BotPassword_ttp = CreateToolTip(
        BotPassword, "An API Key can be generated on the CSU hub website under 'Developer Settings'"
    )




    menu.iconrow += 1
    catsep = ttk.Separator(SettingsFrame, orient=HORIZONTAL)
    catsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
    menu.iconrow += 1
    ObnoxiousCheck = ttk.Checkbutton(
        SettingsFrame, text="  Obnoxious\ndebug mode?", variable=menu.debug
    )
    ObnoxiousCheck.grid(row=menu.iconrow, column=0, rowspan=2, padx=5)
    menu.iconrow += 3
    SaveImg = PhotoImage(file="UI/Save.png")
    SaveButton = ttk.Button(FilterFrame, image=SaveImg, command=SaveFilter)

    SaveButton.image = SaveImg
    SaveButton.grid(row=menu.iconrow, column=7, columnspan=1, pady=5)
    SaveButton_ttp = CreateToolTip(
        SaveButton, "Save Current Filter and Export Settings"
    )

    SaveImg2 = PhotoImage(file="UI/Save.png")
    SaveButton2 = ttk.Button(SettingsFrame, image=SaveImg2, command=SaveFilter)

    SaveButton2.image = SaveImg2
    SaveButton2.grid(row=menu.iconrow, column=0, columnspan=8, pady=5)
    SaveButton_ttp2 = CreateToolTip(
        SaveButton2, "Save Current Filter and Export Settings"
    )

    if menu.faction[0] == 0:
        Wimg = PhotoImage(file="UI//W0.png")
        WardenButton = ttk.Button(
            FilterFrame, image=Wimg, style="EnabledFaction.TButton"
        )
        WardenButton.image = Wimg
    else:
        Wimg = PhotoImage(file="UI//W1.png")
        WardenButton = ttk.Button(
            FilterFrame, image=Wimg, style="DisabledFaction.TButton"
        )
        WardenButton.image = Wimg
    WardenButton["command"] = lambda WardenButton=WardenButton: open_this(
        "W", WardenButton
    )
    WardenButton.grid(row=menu.iconrow, column=0, columnspan=1, pady=5)
    WardenButton_ttp = CreateToolTip(WardenButton, "Enable/Disable Warden-only Items")
    if menu.faction[1] == 0:
        Cimg = PhotoImage(file="UI//C0.png")
        ColonialButton = ttk.Button(
            FilterFrame, image=Cimg, style="EnabledFaction.TButton"
        )
        ColonialButton.image = Cimg
    else:
        Cimg = PhotoImage(file="UI//C1.png")
        ColonialButton = ttk.Button(
            FilterFrame, image=Cimg, style="DisabledFaction.TButton"
        )
        ColonialButton.image = Cimg
    ColonialButton["command"] = lambda ColonialButton=ColonialButton: open_this(
        "C", ColonialButton
    )
    ColonialButton.grid(row=menu.iconrow, column=1, columnspan=1, pady=5)
    ColonialButton_ttp = CreateToolTip(
        ColonialButton, "Enable/Disable Colonial-only Items"
    )
    menu.iconrow += 1
    for i in range(len(sortedicons)):
        # print("comparison", str(icons[i][2]), str(menu.lastcat))
        if str(sortedicons[i][2]) != str(menu.lastcat):
            menu.lastcat = int(sortedicons[i][2])
            menu.iconrow += 1
            try:
                catsep = ttk.Separator(FilterFrame, orient=HORIZONTAL)
                catsep.grid(row=menu.iconrow, columnspan=8, sticky="ew", pady=10)
                menu.iconrow += 1
                catimg = PhotoImage(file="UI//cat" + str(menu.lastcat) + ".png")
                if menu.category[menu.lastcat][1] == 0:
                    catbtn = ttk.Button(
                        FilterFrame, image=catimg, style="EnabledCategory.TButton"
                    )
                else:
                    catbtn = ttk.Button(
                        FilterFrame, image=catimg, style="DisabledCategory.TButton"
                    )
                catbtn.image = catimg
                counter += 1
                catbtn["command"] = lambda i=i, catbtn=catbtn: open_this(
                    str("cat-" + str(sortedicons[i][2])), catbtn
                )
                menu.iconcolumn = 0
                catbtn.grid(
                    row=menu.iconrow,
                    column=menu.iconcolumn,
                    sticky="NSEW",
                    columnspan=8,
                )
                menu.iconrow += 1
                menu.itembuttons.extend((catbtn, "category", sortedicons[i][2]))
                catbtnttp = (
                    "cat"
                    + str(counter)
                    + "_ttp = CreateToolTip(catbtn, '"
                    + str(sortedicons[i][6])
                    + "')"
                )
                exec(catbtnttp)
            except Exception as e:
                print("Exception: ", e)
                print("Category exception")
                logging.info(
                    str(datetime.datetime.now()) + " Category exception " + str(e)
                )
        if os.path.exists("UI//" + str(sortedicons[i][0]) + ".png"):
            img = PhotoImage(file="UI//" + str(sortedicons[i][0]) + ".png")
            if sortedicons[i][4] == 0:
                btn = ttk.Button(FilterFrame, image=img, style="EnabledButton.TButton")
            elif sortedicons[i][4] == 1:
                btn = ttk.Button(
                    FilterFrame, image=img, style="ManualDisabledButton.TButton"
                )
            else:
                btn = ttk.Button(FilterFrame, image=img, style="DisabledButton.TButton")
            counter += 1
            btn.image = img
            # This stuff after the lambda makes sure they're set to the individual values, if I add more, have to be blah=blah before it
            btn["command"] = lambda i=i, btn=btn: open_this(sortedicons[i][0], btn)
            if menu.iconcolumn < 8:
                btn.grid(
                    row=menu.iconrow, column=menu.iconcolumn, sticky="W", padx=2, pady=2
                )
                menu.iconcolumn += 1
            else:
                menu.iconrow += 1
                menu.iconcolumn = 0
                btn.grid(
                    row=menu.iconrow, column=menu.iconcolumn, sticky="W", padx=2, pady=2
                )
                menu.iconcolumn += 1
            # print(btn, sortedicons[i][2])
            tooltiptext = re.sub("'", "", sortedicons[i][5])
            # itembtnttp = ("item" + str(counter) + "_ttp = CreateToolTip(btn, '" + str(sortedicons[i][5]) + "')")
            itembtnttp = (
                "item"
                + str(counter)
                + "_ttp = CreateToolTip(btn, '"
                + tooltiptext
                + "')"
            )
            exec(itembtnttp)
            menu.itembuttons.extend((btn, sortedicons[i][0], sortedicons[i][2]))
    QuitButton = ttk.Button(
        FilterFrame,
        text="Quit",
        style="EnabledButton.TButton",
        command=lambda: StockpilerWindow.quit(),
    )
    QuitButton.grid(row=500, column=0, columnspan=10, sticky="NSEW")
    FilterFrame.update()
    try:
        print(
            "create_window height for Filter canvas should be roughly:",
            str(btn.winfo_y() - 505),
        )
    except Exception as e:
        print("Exception: ", e)
        print("Might not be any buttons")
        logging.info(str(datetime.datetime.now()) + " No buttons? " + str(e))


def SavePickerPosition(x, y):
    menu.PickerX = x
    menu.PickerY = y


def IconCatPicker(image, back):
    global IconCatPickerWindow
    global tempicon
    if back == 1:
        WhatItemWindow.destroy()
    tempicon = image
    root_x = StockpilerWindow.winfo_rootx()
    root_y = StockpilerWindow.winfo_rooty()
    if menu.PickerX != -1:
        win_x = menu.PickerX
        win_y = menu.PickerY
    elif root_x == root_y == -32000:
        win_x = 20
        win_y = 20
    elif root_x < 20:
        win_x = 20
        win_y = 20
    else:
        # This window is so big in its current form that it just needs to be further in the corner
        win_x = root_x - 20
        win_y = root_y - 20

    location = "+" + str(win_x) + "+" + str(win_y)
    IconCatPickerWindow = Toplevel(StockpilerWindow)
    IconCatPickerWindow.geometry(location)
    IconCatPickerFrame = ttk.Frame(IconCatPickerWindow)
    IconCatPickerWindow.resizable(False, False)
    IconCatPickerFrame.pack()
    IconCatPickerFrame.grid_forget()
    iconrow = iconcolumn = 0
    unique_list = []
    counter = 0
    NewIconLabel = ttk.Label(IconCatPickerFrame, text="What category is this item in?")
    NewIconLabel.grid(row=iconrow, column=0, columnspan=5)
    iconrow += 1
    im = Image.fromarray(image)
    bigim = im.resize(size=(200, 200), resample=Image.NEAREST)
    tkimage = ImageTk.PhotoImage(im)
    tkimagebig = ImageTk.PhotoImage(bigim)
    NewIconImage = ttk.Label(IconCatPickerFrame, image=tkimage)
    NewIconImage.image = image
    NewIconImage.grid(row=iconrow, column=0)
    BigIconImage = ttk.Label(IconCatPickerFrame, image=tkimagebig)
    BigIconImage.image = image
    BigIconImage.grid(row=iconrow, column=1, columnspan=4)
    iconrow += 1
    for x in items.data:
        if [x[9], x[8]] not in unique_list:
            unique_list.append([x[9], x[8]])
    for x in unique_list:
        if os.path.exists("UI//cat" + str(x[0]) + ".png"):
            img = PhotoImage(file="UI//cat" + str(x[0]) + ".png")
            btn = ttk.Button(
                IconCatPickerFrame, image=img, style="EnabledButton.TButton"
            )
            counter += 1
            btn.image = img
            # This stuff after the lambda makes sure they're set to the individual values, if I add more, have to be blah=blah before it
            btn["command"] = lambda x=x, btn=btn: WhatItem(image, x[0])
            # btn["command"] = lambda x=x, btn=btn: IndividualOrCrate(items.data[x][0])
            if iconcolumn < 5:
                btn.grid(row=iconrow, column=iconcolumn, sticky="W", padx=2, pady=2)
                iconcolumn += 1
            else:
                iconrow += 1
                iconcolumn = 0
                btn.grid(row=iconrow, column=iconcolumn, sticky="W", padx=2, pady=2)
                iconcolumn += 1
            tooltiptext = re.sub("'", "", x[1])
            itembtnttp = (
                "item"
                + str(counter)
                + "_ttp = CreateToolTip(btn, '"
                + tooltiptext
                + "')"
            )
            exec(itembtnttp)
    IconCatPickerWindow.wait_window()


def WhatItem(image, catnumber):
    global WhatItemWindow
    global tempicon
    IconCatPickerWindow.destroy()
    tempicon = image
    root_x = StockpilerWindow.winfo_rootx()
    root_y = StockpilerWindow.winfo_rooty()
    if menu.PickerX != -1:
        win_x = menu.PickerX
        win_y = menu.PickerY
    elif root_x == root_y == -32000:
        win_x = 20
        win_y = 20
    elif root_x < 20:
        win_x = 20
        win_y = 20
    else:
        # This window is so big in its current form that it just needs to be further in the corner
        win_x = root_x - 20
        win_y = root_y - 20

    location = "+" + str(win_x) + "+" + str(win_y)
    WhatItemWindow = Toplevel(StockpilerWindow)
    WhatItemWindow.geometry(location)
    WhatItemFrame = ttk.Frame(WhatItemWindow)
    WhatItemWindow.resizable(False, False)
    WhatItemFrame.pack()
    WhatItemFrame.grid_forget()
    iconrow = iconcolumn = 0
    NewIconLabel = ttk.Label(WhatItemFrame, text="What item is this?")
    NewIconLabel.grid(row=iconrow, column=0, columnspan=5)
    iconrow += 1
    im = Image.fromarray(image)
    tkimage = ImageTk.PhotoImage(im)
    NewIconImage = ttk.Label(WhatItemFrame, image=tkimage)
    NewIconImage.image = image
    NewIconImage.grid(row=iconrow, column=0)
    bigim = im.resize(size=(200, 200), resample=Image.NEAREST)
    tkimagebig = ImageTk.PhotoImage(bigim)
    BigIconImage = ttk.Label(WhatItemFrame, image=tkimagebig)
    BigIconImage.image = image
    BigIconImage.grid(row=iconrow, column=1, columnspan=4)
    iconrow += 1
    unique_list = []
    counter = 0
    for x in items.data:
        if x[9] == catnumber:
            unique_list.append([x[0], x[3]])
    for x in unique_list:
        print(x)
        if os.path.exists("UI//" + str(x[0]) + ".png"):
            img = PhotoImage(file="UI//" + str(x[0]) + ".png")
            btn = ttk.Button(WhatItemFrame, image=img, style="EnabledButton.TButton")
            counter += 1
            btn.image = img
            # This stuff after the lambda makes sure they're set to the individual values, if I add more, have to be blah=blah before it
            print(x)
            btn["command"] = lambda x=x, btn=btn: IndividualOrCrate(x[0], image)
            if iconcolumn < 11:
                btn.grid(row=iconrow, column=iconcolumn, sticky="W", padx=2, pady=2)
                iconcolumn += 1
            else:
                iconrow += 1
                iconcolumn = 0
                btn.grid(row=iconrow, column=iconcolumn, sticky="W", padx=2, pady=2)
                iconcolumn += 1
            tooltiptext = re.sub("'", "", x[1])
            itembtnttp = (
                "item"
                + str(counter)
                + "_ttp = CreateToolTip(btn, '"
                + tooltiptext
                + "')"
            )
            exec(itembtnttp)
    iconrow += 1
    BackButton = ttk.Button(
        WhatItemFrame,
        text="Back to Category Picker",
        command=lambda: IconCatPicker(image, 1),
    )
    BackButton.grid(row=iconrow, column=0, columnspan=2)
    WhatItemWindow.wait_window()


# def IconPicker(image):
# 	global IconPickerWindow
# 	global tempicon
# 	tempicon = image
# 	root_x = StockpilerWindow.winfo_rootx()
# 	root_y = StockpilerWindow.winfo_rooty()
# 	if menu.PickerX != -1:
# 		win_x = menu.PickerX
# 		win_y = menu.PickerY
# 	elif root_x == root_y == -32000:
# 		win_x = 20
# 		win_y = 20
# 	elif root_x < 20:
# 		win_x = 20
# 		win_y = 20
# 	else:
# 		# This window is so big in its current form that it just needs to be further in the corner
# 		win_x = root_x - 20
# 		win_y = root_y - 20
#
# 	location = "+" + str(win_x) + "+" + str(win_y)
# 	IconPickerWindow = Toplevel(StockpilerWindow)
# 	IconPickerWindow.geometry(location)
# 	IconPickerFrame = ttk.Frame(IconPickerWindow)
# 	IconPickerWindow.resizable(False, False)
# 	IconPickerFrame.pack()
#
# 	IconPickerFrame.grid_forget()
# 	NewIconLabel = ttk.Label(IconPickerFrame, text="What's this?")
# 	NewIconLabel.grid(row=0, column=0, columnspan=2)
# 	im = Image.fromarray(image)
# 	tkimage = ImageTk.PhotoImage(im)
# 	NewIconImage = ttk.Label(IconPickerFrame, image=tkimage)
# 	NewIconImage.image = image
# 	NewIconImage.grid(row=0, column=2)
# 	SavePositionBtn = ttk.Button(IconPickerFrame, text="Save Window Position", style="EnabledButton.TButton", command=lambda: SavePickerPosition(IconPickerWindow.winfo_x(), IconPickerWindow.winfo_y()))
# 	SavePositionBtn.grid(row=0, column=5, columnspan=5)
# 	iconcolumn = 0
# 	iconrow = 1
# 	counter = 0
# 	temptime = datetime.datetime.now()
# 	for x in range(len(items.data)):
# 		if os.path.exists("UI//" + str(items.data[x][0]) + ".png"):
# 			img = PhotoImage(file="UI//" + str(items.data[x][0]) + ".png")
# 			btn = ttk.Button(IconPickerFrame, image=img, style="EnabledButton.TButton")
# 			counter += 1
# 			btn.image = img
# 			# This stuff after the lambda makes sure they're set to the individual values, if I add more, have to be blah=blah before it
# 			btn["command"] = lambda x=x, btn=btn: IndividualOrCrate(items.data[x][0])
# 			if iconcolumn < 18:
# 				btn.grid(row=iconrow, column=iconcolumn, sticky="W", padx=2, pady=2)
# 				iconcolumn += 1
# 			else:
# 				iconrow += 1
# 				iconcolumn = 0
# 				btn.grid(row=iconrow, column=iconcolumn, sticky="W", padx=2, pady=2)
# 				iconcolumn += 1
# 			tooltiptext = re.sub('\'', '', items.data[x][3])
# 			itembtnttp = ("item" + str(counter) + "_ttp = CreateToolTip(btn, '" + tooltiptext + "')")
# 			exec(itembtnttp)
# 	print("Took this long to make icon picker window:", datetime.datetime.now() - temptime)
# 	IconPickerWindow.wait_window()


def IndividualOrCrate(num, image):
    WhatItemWindow.destroy()
    global IndOrCrateWindow
    root_x = StockpilerWindow.winfo_rootx()
    root_y = StockpilerWindow.winfo_rooty()
    if menu.PickerX != -1:
        win_x = menu.PickerX
        win_y = menu.PickerY
    elif root_x == root_y == -32000:
        win_x = 20
        win_y = 20
    elif root_x < 20:
        win_x = 20
        win_y = 20
    else:
        win_x = root_x - 20
        win_y = root_y - 20
    location = "+" + str(win_x) + "+" + str(win_y)
    IndOrCrateWindow = Toplevel(StockpilerWindow)
    IndOrCrateWindow.geometry(location)
    IndOrCrateWindow.resizable(False, False)
    IndOrCrateFrame = ttk.Frame(IndOrCrateWindow, style="TFrame")
    IndOrCrateFrame.pack()
    ForLabel = ttk.Label(IndOrCrateFrame, text="For:")
    ForLabel.grid(row=0, column=0)
    YouSelectedLabel = ttk.Label(IndOrCrateFrame, text="You\nSelected:")
    YouSelectedLabel.grid(row=0, column=1)
    im = Image.fromarray(image)
    tkimage = ImageTk.PhotoImage(im)
    NewIconImage = ttk.Label(IndOrCrateFrame, image=tkimage)
    NewIconImage.image = tempicon
    NewIconImage.grid(row=1, column=0)
    bigim = im.resize(size=(200, 200), resample=Image.NEAREST)
    tkimagebig = ImageTk.PhotoImage(bigim)
    BigIconImage = ttk.Label(IndOrCrateFrame, image=tkimagebig)
    BigIconImage.image = image
    BigIconImage.grid(row=2, column=0)
    UIimage = PhotoImage(file="Compare//" + str(num) + ".png")
    SelectedImage = ttk.Label(IndOrCrateFrame, image=UIimage)
    SelectedImage.image = UIimage
    SelectedImage.grid(row=1, column=1, rowspan=2)
    IndividualButton = ttk.Button(
        IndOrCrateFrame,
        text="Individual",
        style="EnabledButton.TButton",
        command=lambda: SaveIcon(num, 0, tempicon),
    )
    IndividualButton.grid(row=5, column=0)
    CrateButton = ttk.Button(
        IndOrCrateFrame,
        text="Crate",
        style="EnabledButton.TButton",
        command=lambda: SaveIcon(num, 1, tempicon),
    )
    CrateButton.grid(row=5, column=1)
    TryAgainButton = ttk.Button(
        IndOrCrateFrame,
        text="Pick a different icon?",
        style="EnabledButton.TButton",
        command=lambda: BackToPicker(tempicon),
    )
    TryAgainButton.grid(row=10, column=0, columnspan=2)
    IndOrCrateWindow.wait_window()


def BackToPicker(image):
    global IndOrCrateWindow
    IndOrCrateWindow.destroy()
    IconCatPicker(image, 0)


def SaveIcon(num, type, image):
    global IndOrCrateWindow
    IndOrCrateWindow.destroy()
    if type == 0:
        name = str(num) + ".png"
    else:
        name = str(num) + "C.png"
    if menu.Set.get() == 0:
        save = "CheckImages//Default//" + name
    else:
        save = "CheckImages//Modded//" + name
    print("save:", save)
    cv2.imwrite(save, image)


def open_this(myNum, btn):
    if str(btn["style"]) == "EnabledButton.TButton":
        btn.configure(style="ManualDisabledButton.TButton")
        for item in range(len(items.data)):
            if str(items.data[item][0]) == str(myNum):
                items.data[item][19] = 1
                print(items.data[item][19])
    elif str(btn["style"]) == "ManualDisabledButton.TButton":
        btn.configure(style="EnabledButton.TButton")
        for item in range(len(items.data)):
            if str(items.data[item][0]) == str(myNum):
                items.data[item][19] = 0
                print(items.data[item][19])
    elif str(btn["style"]) == "EnabledCategory.TButton":
        btn.config(style="DisabledCategory.TButton")
        menu.category[int(myNum[4:5])][1] = 1
        print("category number was 0")
        for item in range(len(items.data)):
            if str(items.data[item][9]) == str(myNum[4:5]):
                if str(items.data[item][19]) == str(0):
                    items.data[item][19] = 2
        CreateButtons("blah")
    elif str(btn["style"]) == "DisabledCategory.TButton":
        btn.config(style="EnabledCategory.TButton")
        menu.category[int(myNum[4:5])][1] = 0
        print("category number was 1")
        for item in range(len(items.data)):
            if str(items.data[item][9]) == str(myNum[4:5]):
                if str(items.data[item][19]) == str(2):
                    items.data[item][19] = 0
        CreateButtons("blah")
    elif myNum == str("W"):
        if str(btn["style"]) == "EnabledFaction.TButton":
            btn.config(style="DisabledFaction.TButton")
            menu.faction[0] = 1
            for item in range(len(items.data)):
                if items.data[item][7] == "Warden" and str(items.data[item][19]) == "0":
                    items.data[item][19] = 3
        else:
            btn.config(style="EnabledFaction.TButton")
            menu.faction[0] = 0
            for item in range(len(items.data)):
                if items.data[item][7] == "Warden" and str(items.data[item][19]) == "3":
                    items.data[item][19] = 0
        CreateButtons("blah")
    elif myNum == str("C"):
        if str(btn["style"]) == "EnabledFaction.TButton":
            btn.config(style="DisabledFaction.TButton")
            menu.faction[1] = 1
            for item in range(len(items.data)):
                if (
                    items.data[item][7] == "Colonial"
                    and str(items.data[item][19]) == "0"
                ):
                    items.data[item][19] = 3
        else:
            btn.config(style="EnabledFaction.TButton")
            menu.faction[1] = 0
            for item in range(len(items.data)):
                if (
                    items.data[item][7] == "Colonial"
                    and str(items.data[item][19]) == "3"
                ):
                    items.data[item][19] = 0
        CreateButtons("blah")


if os.path.exists("Config.txt"):
    with open("Config.txt") as file:
        content = file.readlines()
    content = [x.strip() for x in content]
    try:
        print("Attempting to load from Config.txt")
        logging.info(
            str(datetime.datetime.now()) + " Attempting to load from config.txt"
        )
        menu.CSVExport.set(int(content[0]))
        menu.XLSXExport.set(int(content[1]))
        menu.ImgExport.set(int(content[2]))
        menu.Set.set(int(content[3]))
        menu.Learning.set(int(content[4]))
        menu.updateAPI.set(int(content[5]))
        menu.APIHost.set(content[6])
        menu.APIKey.set(content[7])
    except Exception as e:
        print("Exception: ", e)
        logging.info(
            str(datetime.datetime.now())
            + " Loading from config.txt failed, setting defaults"
        )
        menu.CSVExport.set(0)
        menu.XLSXExport.set(0)
        menu.ImgExport.set(1)
        menu.Set.set(0)
        menu.Learning.set(0)
    try:
        print("Attempting to load hotkeys from config.txt")
        logging.info(
            str(datetime.datetime.now())
            + " Attempting to load from hotkeys from config.txt"
        )
        menu.grabhotkey.set(content[8])
        menu.scanhotkey.set(content[9])
        menu.grabhotkeystring = menu.grabhotkey.get()
        menu.scanhotkeystring = menu.scanhotkey.get()
        menu.grabshift.set(content[11][0])
        menu.grabctrl.set(content[11][1])
        menu.grabalt.set(content[11][2])
        menu.grabmods = (
            str(menu.grabshift.get())
            + str(menu.grabctrl.get())
            + str(menu.grabalt.get())
        )
        menu.scanshift.set(content[12][0])
        menu.scanctrl.set(content[12][1])
        menu.scanalt.set(content[12][2])
        menu.scanmods = (
            str(menu.scanshift.get())
            + str(menu.scanctrl.get())
            + str(menu.scanalt.get())
        )
    except Exception as e:
        print("Exception: ", e)
        print(
            "Failed to load hotkeys from config.txt, setting them to defaults of f2, f3"
        )
        logging.info(
            str(datetime.datetime.now())
            + " No custom hotkeys in config.txt, setting defaults of f2, f3"
        )
        menu.grabhotkey.set("f2")
        menu.scanhotkey.set("f3")
        menu.grabhotkeystring = menu.grabhotkey.get()
        menu.scanhotkeystring = menu.scanhotkey.get()
        menu.grabshift.set(0)
        menu.grabctrl.set(0)
        menu.grabalt.set(0)
        menu.grabmods = "000"
        menu.scanshift.set(0)
        menu.scanctrl.set(0)
        menu.scanalt.set(0)
        menu.scanmods = "000"
else:
    menu.CSVExport.set(0)
    menu.XLSXExport.set(0)
    menu.ImgExport.set(1)
    menu.Set.set(0)
    menu.Learning.set(0)


def SetHotkeys(self):
    # print(menu.grabmods, menu.scanmods)
    clear_hotkeys()
    if menu.grabmods[0] == "0":
        grabshift = ""
    else:
        grabshift = '"shift",'
    if menu.grabmods[1] == "0":
        grabctrl = ""
    else:
        grabctrl = '"control",'
    if menu.grabmods[2] == "0":
        grabalt = ""
    else:
        grabalt = '"alt",'
    if menu.scanmods[0] == "0":
        scanshift = ""
    else:
        scanshift = '"shift",'
    if menu.scanmods[1] == "0":
        scanctrl = ""
    else:
        scanctrl = '"control",'
    if menu.scanmods[2] == "0":
        scanalt = ""
    else:
        scanalt = '"alt",'
    bindingsstring = (
        "menu.bindings = [[["
        + grabshift
        + grabctrl
        + grabalt
        + '"'
        + menu.grabhotkeystring
        + '"], None, GrabStockpileImage],[['
        + scanshift
        + scanctrl
        + scanalt
        + '"'
        + menu.scanhotkeystring
        + '"], None, LearnOrNot],]'
    )
    exec(bindingsstring)
    register_hotkeys(menu.bindings)
    start_checking_hotkeys()
    if menu.grabhotkeystring == menu.scanhotkeystring:
        popup("DuplicateHotkeys")


def ResetHotkeys():
    menu.grabshift.set(0)
    menu.grabctrl.set(0)
    menu.grabalt.set(0)
    menu.grabmods = "000"
    menu.grabhotkey.set("f2")
    menu.grabhotkeystring = "f2"
    menu.scanshift.set(0)
    menu.scanctrl.set(0)
    menu.scanalt.set(0)
    menu.scanmods = "000"
    menu.scanhotkey.set("f3")
    menu.scanhotkeystring = "f3"
    SetHotkeys("")


CreateButtons("")

SetHotkeys("")

StockpilerWindow.mainloop()
