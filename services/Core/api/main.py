import os
from datetime import datetime

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import EmailStr

from database.db import user_collection
from database.models.user import User, UserCreate

load_dotenv()
port = os.getenv('CORE_PORT')

# Creates app instance
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/auth/register")
async def register(user: UserCreate):
    user_db = await user_collection.find_one({"email": user.email})
    if not user_db:
        user_db = User(
            username=user.username,
            email=EmailStr(user.email),
            phone_number=user.phone_number,
            quotes=[],
            created_at=datetime.now(),
        )
        encoded_task = jsonable_encoder(user_db)
        u = await user_collection.insert_one(encoded_task)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=u.inserted_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=user_db["_id"])


# @app.get("/create/quotes/{user_id}", response_description="Add new quote", response_model=Quote)
# async def create_quote(user_id: str):
#     user_id = await create_user_if_not_exist(user_id)
#     quote_class = Quotes(source=random.choice(list(Source)))
#     quote = quote_class.get_new_quote()
#     quote.user_ids.append(PyObjectId(user_id))
#     encoded_task = jsonable_encoder(quote)
#     q = await quotes_collection.insert_one(encoded_task)
#     created_q = await quotes_collection.find_one({"_id": q.inserted_id})
#     user = await user_collection.find_one({"_id": user_id})
#     user["quotes"].append(q.inserted_id)
#     await user_collection.replace_one({"_id": user_id}, user)
#     return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": created_q})
#
#
# @app.get("/get/quotes/{user_id}", response_description="Get users quotes", response_model=List[Quote])
# async def get_user_quotes(user_id: str):
#     user = await user_collection.find_one({"_id": user_id})
#     if not user:
#         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "User not found"})
#     quotes = []
#     for quote_id in user["quotes"]:
#         quote = await quotes_collection.find_one({"_id": quote_id})
#         quotes.append(quote)
#     return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": quotes})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=int(port), reload=True)
