import os

import motor.motor_asyncio
from dotenv import load_dotenv
from pymongo.collection import Collection


def initiate_mongo_client(collection: str) -> Collection:
    load_dotenv()
    client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGOURI"])
    db = client[os.getenv("MOTIME_DB")]
    return db.get_collection(os.getenv(collection))


# Connect to the MongoDB database
quotes_collection = initiate_mongo_client("QUOTE_COLLECTION")
user_collection = initiate_mongo_client("USER_COLLECTION")
