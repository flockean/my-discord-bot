import requests

api_url = "https://api.nekosapi.com/v3/"
best_neko_api = "https://nekos.best/api/v2/"


def get_api(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

def neko_best(emote):
    data = get_api(best_neko_api + str(emote))
    for item in data['results']:
        return item['url']
