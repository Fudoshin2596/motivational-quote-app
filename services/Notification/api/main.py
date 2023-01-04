import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.Notification.notification import NotificationClient

load_dotenv()
port = os.getenv('NOTIFICATION_PORT')

# Creates app instance
app = FastAPI()


class NotificationRequest(BaseModel):
    quote: str
    author: str
    recipient: str


@app.post("/notify")
async def notify(request: NotificationRequest):
    twilio_client = NotificationClient(quote=request.quote, author=request.author, recipient=request.recipient)
    sms_id = twilio_client.send_sms()
    return JSONResponse(status_code=status.HTTP_200_OK, content=sms_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(port), reload=True)
