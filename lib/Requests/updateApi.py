import requests

def updateApi(menu, items, ThisStockpileName):
    if menu.updateAPI.get() == 1:
        requestObj = {
            "key": menu.APIKey.get(),
        }
        

        data = []
        for x in items.sortedcontents:
            data.append({"id":x[0], "item":x[1], "amount": x[2]})
            requestObj["data"] = data


            finData = {"name": ThisStockpileName, "contents": data }

            print("Bot Data", finData)

            print(requestObj)

            try:
                r = requests.post(menu.BotHost.get()+'?key='+menu.APIKey, finData)
                response = r.json()
                print(response)
                print("sending")
            except Exception as e:
                print("There was an error connecting to the API")
                print("Exception: ", e)
