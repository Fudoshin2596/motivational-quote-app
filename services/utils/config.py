import os

import httpx
from dotenv import load_dotenv

load_dotenv()

local_host = "127.0.0.1"
core_port = int(os.getenv('CORE_PORT'))
quote_port = int(os.getenv('QUOTE_PORT'))
prediction_port = int(os.getenv('PREDICTION_PORT'))
notification_port = int(os.getenv('NOTIFICATION_PORT'))

prediction_model_path = "model/text_classification.pkl"

httpclient = httpx.AsyncClient(http2=True)
