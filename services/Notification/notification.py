import os

from attr import define, field
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()


@define
class NotificationClient:
    recipient: str
    quote: str = field(init=True, default="")
    author: str = field(init=True, default="")
    _client: Client = field(init=False, default=Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN')))

    def format(self) -> str:
        return f"{self.quote} | Author: {self.author}"

    def send_sms(self) -> str:
        """ sends quote using twilio API"""
        body = self.format()
        message = self._client.messages.create(
            to=self.recipient,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            body=body
        )
        return message.sid


if __name__ == "__main__":
    twilio_client = NotificationClient("Hello World", "Joel", os.getenv("Target_number1"))
    twilio_client.send_sms()
