import random

import uvicorn
from fastapi import FastAPI
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from database.models.quote import Quote
from services.Quotes.quote_manager import Quotes, Source
from services.utils.config import quote_port, local_host

app = FastAPI()


@app.get("/quote", response_model=Quote)
async def quote():
    quote_class = Quotes(source=random.choice(list(Source)))
    q = await quote_class.get_new_quote()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(q))


if __name__ == "__main__":
    uvicorn.run("main:app", host=local_host, port=quote_port, reload=True)
