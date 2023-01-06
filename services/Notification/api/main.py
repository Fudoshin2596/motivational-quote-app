import uvicorn
from fastapi import FastAPI
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.Notification.notification import NotificationClient
from services.utils.config import notification_port, local_host

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
    uvicorn.run("main:app", host=local_host, port=notification_port, reload=True)
