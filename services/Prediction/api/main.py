import joblib
import uvicorn
from fastapi import FastAPI
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.utils.config import prediction_port, local_host, prediction_model_path

app = FastAPI()


class QuoteRequest(BaseModel):
    quote: str


def predict(quote: str, path=prediction_model_path):
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
    uvicorn.run("main:app", host=local_host, port=prediction_port, reload=True)
