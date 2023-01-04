import os
import random

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from database.models.quote import Quote
from services.Quotes.quote_manager import Quotes, Source

load_dotenv()
port = os.getenv('QUOTE_PORT')

# Creates app instance
app = FastAPI()


@app.get("/quote", response_model=Quote)
def quote():
    quote_class = Quotes(source=random.choice(list(Source)))
    Q = jsonable_encoder(quote_class.get_new_quote())
    return JSONResponse(status_code=status.HTTP_200_OK, content=Q)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(port), reload=True)
