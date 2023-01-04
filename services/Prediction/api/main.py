import os

import joblib
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()
port = os.getenv('PREDICTION_PORT')

# Creates app instance
app = FastAPI()


class QuoteRequest(BaseModel):
    quote: str


def predict(quote: str, path='model/text_classification.pkl'):
    model = open(path, 'rb')
    pipeline = joblib.load(model)
    labels_text = ['aspirations', 'emotional', 'personal', 'thoughtful', 'work']
    ans = pipeline.predict([quote])
    return labels_text[int(ans)]


@app.post("/predict")
async def public(quote_request: QuoteRequest):
    prediction = predict(quote_request.quote)
    return JSONResponse(status_code=status.HTTP_200_OK, content=prediction)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(port), reload=True)
