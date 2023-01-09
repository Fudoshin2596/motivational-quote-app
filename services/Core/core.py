import asyncio
import random

from attrs import define
from fastapi.encoders import jsonable_encoder

from database.db import user_collection, quotes_collection
from database.models.quote import Quote
from services.Notification.notification import NotificationClient
from services.Prediction.main import get_prediction
from services.Quotes.quote_manager import Quotes, Source


@define
class NotificationRequest:
    quote: str
    author: str
    recipient: str


@define
class QuoteRequest:
    quote: str


async def notify(request: NotificationRequest) -> str:
    twilio_client = NotificationClient(quote=request.quote, author=request.author, recipient=request.recipient)
    sms_id = twilio_client.send_sms()
    return sms_id


async def predict(quote_request: QuoteRequest) -> str:
    prediction = get_prediction(quote_request.quote)
    return prediction


async def get_quote() -> Quote:
    quote_class = Quotes(source=random.choice(list(Source)))
    q = await quote_class.get_new_quote()
    return q


# noinspection HttpUrlsUsage
async def run():
    # get quote
    quote: Quote = await get_quote()
    # predict category
    quote.category = await predict(QuoteRequest(quote=quote.quote))
    # get all users from db
    all_users = await user_collection.find().to_list(None)
    for user in all_users:
        user_id = user["_id"]
        # send quote to user
        n = await notify(NotificationRequest(quote=quote.quote, author=quote.author, recipient=user['phone_number']))
        if n:
            # update quote with user id
            quote.user_ids.append(user_id)
            # save quote to db
            encoded_q = jsonable_encoder(quote)
            q = await quotes_collection.insert_one(encoded_q)
            # update user with quote id
            user["quotes"].append(q.inserted_id)
            await user_collection.replace_one({"_id": user_id}, user)
            print(f'Quote {quote.quote} sent to {user["phone_number"]}')
        else:
            print('Failed to send quote to user', n)


if __name__ == '__main__':
    asyncio.run(run())
