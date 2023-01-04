from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field

from backend.database.models.mongodb import PyObjectId


class Quote(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(default_factory=PyObjectId, alias="user_id")
    author: str
    quote: str
    category: str
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
