import random
from datetime import datetime
from typing import List

import uvicorn
from fastapi import Depends, Request
from fastapi import FastAPI
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from pydantic import EmailStr

from database.models.user import User, UserCreate
from database.db import quotes_collection, user_collection
from database.models.mongodb import PyObjectId
from database.models.quote import Quote
from services.quote_manager.quote_manager import Quote_from_twitter, Quote_from_Api

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
manager = LoginManager("DEFAULT_SETTINGS.secret", "/auth/token")


@manager.user_loader()
async def get_user(email: str):
    user = await user_collection.find_one({"email": email})
    return user if user else None


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get("/auth")
def auth():
    with open("templates/auth.html", 'r') as f:
        return HTMLResponse(content=f.read())


@app.post("/auth/register")
async def register(user: UserCreate):
    user_db = User(
        name=user.username,
        email=EmailStr(user.email),
        password=user.password,
        quotes=[],
        created_at=datetime.now(),
    )
    encoded_task = jsonable_encoder(user_db)
    u = await user_collection.insert_one(encoded_task)
    created_u = await quotes_collection.find_one({"_id": u.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_u)


@app.post("/auth/token")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = await get_user(email)  # we are using the same function to retrieve the user
    print(user)
    if not user:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif password != user['password']:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data=dict(sub=email))
    return JSONResponse(status_code=status.HTTP_200_OK, content={'access_token': access_token, 'token_type': 'bearer', 'user_id': str(user['_id'])})


@app.get("/private")
def private_route(user=Depends(manager)):
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": f"Welcome {user['email']}"})


async def create_user_if_not_exist(user_id: str) -> str:
    user = await user_collection.find_one({"_id": user_id})
    if not user:
        user_db = User(
            name="Test User",
            email=EmailStr("a.joeljr@hotmail.com"),
            password="test",
            quotes=[],
            created_at=datetime.now(),
        )
        encoded_task = jsonable_encoder(user_db)
        u = await user_collection.insert_one(encoded_task)
        return str(u.inserted_id)
    return user_id


@app.get("/create/quotes/{user_id}", response_description="Add new quote", response_model=Quote)
async def create_quote(user_id: str):
    user_id = await create_user_if_not_exist(user_id)
    quote_class = random.choice([Quote_from_twitter(), Quote_from_Api()])
    aut = None
    quote = None
    while aut is None or quote is None:
        aut, quote = quote_class.getInfo()

    quote = Quote(
        author=aut,
        quote=quote,
        category="random",
        user_id=PyObjectId(user_id),
        created_at=datetime.now(),
    )
    encoded_task = jsonable_encoder(quote)
    q = await quotes_collection.insert_one(encoded_task)
    created_q = await quotes_collection.find_one({"_id": q.inserted_id})
    user = await user_collection.find_one({"_id": user_id})
    user["quotes"].append(q.inserted_id)
    await user_collection.replace_one({"_id": user_id}, user)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": created_q})


@app.get("/get/quotes/{user_id}", response_description="Get users quotes", response_model=List[Quote])
async def get_user_quotes(user_id: str):
    user = await user_collection.find_one({"_id": user_id})
    if not user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "User not found"})
    quotes = []
    for quote_id in user["quotes"]:
        quote = await quotes_collection.find_one({"_id": quote_id})
        quotes.append(quote)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": quotes})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
