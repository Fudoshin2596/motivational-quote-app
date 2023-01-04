import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
port = os.getenv('CORE_PORT')

# Creates app instance
app = FastAPI()


@app.get("/api/public")
def public():
    """No access token required to access this route"""

    result = {
        "status": "success",
        "msg": ("Hello from a public endpoint! You don't need to be "
                "authenticated to see this.")
    }
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(port), reload=True)
