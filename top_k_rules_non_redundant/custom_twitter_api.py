import requests
import os
import json
import credentials

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {credentials.BEARER_TOKEN}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def search_tweets(search_query, max_results = '10'):
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    
    # https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent
    query_params = {'query': search_query , 'tweet.fields': 'lang', 'max_results': max_results}

    json_response = connect_to_endpoint(search_url, query_params)
    tweets = []
    for i in range(len(json_response['data'])):
        tweets.append(tweet(json_response['data'][i]))

    return tweets

class tweet:
    def __init__(self, json_data):
        self.id = json_data['id']
        self.lang = json_data['lang']
        # el texto se guarda como un array de string, por lo que es posible acceder a cada palabra utilizando el operador []
        self.text = json_data['text'].split()
