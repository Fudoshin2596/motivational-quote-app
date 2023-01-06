from datetime import datetime
from typing import List

import uvicorn
from fastapi import FastAPI
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import EmailStr

from database.db import user_collection, quotes_collection
from database.models.quote import Quote
from database.models.user import User, UserCreate
from services.utils.config import core_port, local_host

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


@app.get("/quotes/{user_email}", response_model=List[Quote])
async def get_user_quotes(user_email: str):
    user = await user_collection.find_one({"email": user_email})
    if not user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"data": []})
    quotes = []
    for quote_id in user["quotes"]:
        quote = await quotes_collection.find_one({"_id": quote_id})
        quotes.append(quote)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": quotes})


if __name__ == "__main__":
    uvicorn.run("main:app", host=local_host, port=core_port, reload=True)
