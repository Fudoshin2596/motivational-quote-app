import json
import os
import random
import re
from abc import abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any, List

import requests
from attrs import define, field
from dotenv import load_dotenv

from database.models.quote import Quote

load_dotenv()


class Source(str, Enum):
    API = "API"
    TWITTER = "TWITTER"


@define
class QuoteResponse:
    quote: str = field(init=True, default="")
    author: str = field(init=True, default="")

    def __attrs_post_init__(self):
        self.quote = self.quote.strip()
        self.author = self.author.strip()

    @property
    def isvalid(self) -> bool:
        return all([self.quote, self.author])


@define
class QuoteFromApi:
    url: Optional[str] = field(init=False, default=os.getenv('XRAPIDURL'))
    querystring: Dict[str, str] = field(init=False, default={"language_code": "en"})
    headers: Dict[str, str] = field(
        init=False,
        default={'x-rapidapi-host': os.getenv('XRAPIDHOST'), 'x-rapidapi-key': os.getenv('XRAPIDKEY')}
    )

    def get_response(self) -> Dict[str, Any]:
        response = requests.get(self.url, headers=self.headers, params=self.querystring)
        return json.loads(response.text)

    def get_quote(self) -> QuoteResponse:
        res = self.get_response()
        org = res.get('originator')
        return QuoteResponse(
            quote=res.get('content', ""),
            author=org.get('name') if org else ""
        )


@define
class QuoteFromTwitter:
    auth: Optional[str] = field(init=False, default=os.getenv("Twitter_BEARER_TOKEN"))
    headers: Dict[str, str] = field(init=False, factory=dict)

    def __attrs_post_init__(self):
        self.headers = {"Authorization": "Bearer {}".format(self.auth)}

    @staticmethod
    def catch(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (TypeError, AttributeError) as e:
            pass

    @staticmethod
    def create_url() -> str:
        """
        # Tweet fields are adjustable.
        # Options include:
            # attachments, author_id, context_annotations,
            # conversation_id, created_at, entities, geo, id,
            # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
            # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
                # source, text, and withheld
        """
        target = random.choice(['MomentumdashQ', 'LeadershipQuote', 'BrainyQuote', 'UpliftingQuotes', 'GreatestQuotes'])
        return f"https://api.twitter.com/2/tweets/search/recent?query=from:{target}&tweet.fields=text"

    @staticmethod
    def connect_to_endpoint(url, headers) -> Dict[str, Any]:
        response = requests.request("GET", url, headers=headers)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    def get_tweet(self) -> List[QuoteResponse]:
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
                        aut = ""
                    tweets_quote.append(quote)
                    tweets_aut.append(aut)
                working = True
            except KeyError:
                working = False
        return [QuoteResponse(quote=x or "", author=y or "") for x, y in zip(tweets_quote, tweets_aut)]

    def get_quote(self) -> QuoteResponse:
        tweet_list = self.get_tweet()
        for quote_response in tweet_list:
            if quote_response.isvalid:
                return quote_response
        return QuoteResponse()


@define
class Quotes:
    source: Source
    _quote_from_api: QuoteFromApi = field(init=False, default=QuoteFromApi())
    _quote_from_twitter: QuoteFromTwitter = field(init=False, default=QuoteFromTwitter())

    def get_new_quote(self) -> Quote:
        quote_response = QuoteResponse()
        while not quote_response.isvalid:
            quote_response = self.get_quote(self.source)
        return Quote(
            author=quote_response.author,
            quote=quote_response.quote,
            category=None,
            user_ids=[],
            created_at=datetime.now(),
        )

    def make_event(self) -> Dict[str, str]:
        """
        formats quote into a lambda event structure
        """
        event_dict: Dict[str, str] = {}
        quote_response = QuoteResponse()
        while not quote_response.isvalid:
            quote_response = self.get_quote(self.source)
        event_dict["author"] = quote_response.author
        event_dict["quote"] = quote_response.quote
        return event_dict

    @abstractmethod
    def get_quote(self, source: Source) -> QuoteResponse:
        if source == Source.API:
            return self._quote_from_api.get_quote()
        return self._quote_from_twitter.get_quote()


if __name__ == '__main__':
    quote_class = Quotes(source=random.choice(list(Source)))
    quote = quote_class.get_new_quote()
    print(quote)
