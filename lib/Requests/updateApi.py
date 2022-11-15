import requests

def updateApi(menu, items):
    if menu.updateAPI.get() == 1:
        requestObj = {
            "key": menu.APIKey.get(),
        }

        data = []
        for x in items.sortedcontents:
            data.append({"id":x[0], "item":x[1], "amount": x[2]})
            requestObj["data"] = data
            print("Bot Data", data)

            print(requestObj)

            try:
                r = requests.post(menu.BotHost.get()+'?host='+menu.APIKey, data)
                response = r.json()
                print(response)
                print("sending")
            except Exception as e:
                print("There was an error connecting to the API")
                print("Exception: ", e)
