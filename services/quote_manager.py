import json
import os
import random
import re

import requests
from dotenv import load_dotenv

load_dotenv()

Twitter_auth = os.getenv("Twitter_BEARER_TOKEN")
XRAPIDURL = os.getenv('XRAPIDURL')
xrapidapihost = os.getenv('XRAPIDHOST')
xrapidapikey = os.getenv('XRAPIDKEY')


class Quotes:
    def getInfo(self):
        author, quote = self.get_quote()
        return author, quote

    def make_event(self):
        """
        formats quote into a lambda event structure
        """
        event_dict = {}
        quote = ""
        while quote == "":
            aut, quote = self.get_quote()
        event_dict["author"] = aut
        event_dict["quote"] = quote
        return event_dict

    def catch(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (TypeError, AttributeError) as e:
            pass


class Quote_from_Api(Quotes):
    def __init__(self):
        self.url = XRAPIDURL
        self.querystring = {"language_code": "en"}
        self.headers = {
            'x-rapidapi-host': xrapidapihost,
            'x-rapidapi-key': xrapidapikey
        }

    def get_response(self):
        response = requests.get(self.url, headers=self.headers, params=self.querystring)
        res = json.loads(response.text)
        return res

    def get_quote(self):
        res = self.get_response()
        quote = res['content']
        aut = res['originator']['name']
        return aut, quote


class Quote_from_twitter(Quotes):
    def __init__(self):
        self.auth = Twitter_auth
        self.headers = {"Authorization": "Bearer {}".format(self.auth)}

    def create_url(self):
        """
            # Tweet fields are adjustable.
            # Options include:
                # attachments, author_id, context_annotations,
                # conversation_id, created_at, entities, geo, id,
                # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
                # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
                # source, text, and withheld
        """
        target_list = ['MomentumdashQ', 'LeadershipQuote', 'BrainyQuote', 'UpliftingQuotes', 'GreatestQuotes']
        target = random.choice(target_list)
        query = f"from:{target}"
        tweet_fields = "tweet.fields=text"
        url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&{tweet_fields}"
        return url

    def connect_to_endpoint(self, url, headers):
        response = requests.request("GET", url, headers=headers)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    def get_tweet(self):
        working = False
        tweets_quote = []
        tweets_aut = []
        while working is False:
            try:
                url = self.create_url()
                json_response = self.connect_to_endpoint(url, self.headers)
                for response in json_response['data']:
                    regex_q = r'(.*?)(?=(\-|\"|\~))'
                    regex_a = r'(?<=(\-|\~))(.*?)(?=(\#|\"|(http)|\n|\@))'
                    test_str = response['text']
                    try:
                        quote = re.search(regex_q, test_str).group(0)
                    except AttributeError:
                        continue
                    try:
                        aut = re.search(regex_a, test_str).group(0)
                    except AttributeError:
                        aut = None
                    tweets_quote.append(quote)
                    tweets_aut.append(aut)
                working = True
            except KeyError:
                working = False
        tweets_list = [(x, y) for x in tweets_quote for y in tweets_aut]
        return tweets_list

    def get_quote(self):
        tweet_list = self.get_tweet()
        quotetup = random.choice(tweet_list)
        quote = quotetup[0]
        aut = quotetup[1]
        return aut, quote


if __name__ == '__main__':
    quote_class = Quote_from_twitter()
    quote_class = Quote_from_Api()
    aut, quote = quote_class.getInfo()
    print(aut, quote)
