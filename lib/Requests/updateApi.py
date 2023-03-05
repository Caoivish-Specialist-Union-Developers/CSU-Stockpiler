import requests
def updateApi(menu, items, ThisStockpileName):
    if menu.updateAPI.get() == 1:
        
        data = []
        for x in items.sortedcontents:
            data.append({"id":x[0], "item":x[1], "amount": x[2]})


        finData = {"name": ThisStockpileName, "contents": data }

        print("Bot Data", finData)

        print(menu.APIHost.get()+'?key='+menu.APIKey.get(), finData)

        try:
            r = requests.post(menu.APIHost.get()+'?key='+menu.APIKey.get(), json=finData)
            response = r
            print(response)
            print("sending")
        except Exception as e:
            print("There was an error connecting to the API")
            print("Exception: ", e)
