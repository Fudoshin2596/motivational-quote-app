import asyncio

from fastapi.encoders import jsonable_encoder

from database.db import user_collection, quotes_collection
from database.models.quote import Quote
from services.utils.config import quote_port, local_host, httpclient, prediction_port, notification_port


# noinspection HttpUrlsUsage
async def run():
    # get quote
    q = await httpclient.get(f'http://{local_host}:{quote_port}/quote')
    quote = Quote(**q.json())
    # predict category
    c = await httpclient.post(f'http://{local_host}:{prediction_port}/predict', json={'quote': quote.quote})
    quote.category = c.text
    # get all users from db
    all_users = await user_collection.find().to_list(None)
    for user in all_users:
        user_id = user["_id"]
        # send quote to user
        n = await httpclient.post(
            f'http://{local_host}:{notification_port}/notify',
            json={'quote': quote.quote, 'author': quote.author, 'recipient': user['phone_number']}
        )
        if n.text:
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
