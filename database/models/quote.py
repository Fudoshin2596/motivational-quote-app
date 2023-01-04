from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from database.models.common import PyObjectId


class Quote(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_ids: List[PyObjectId] = Field(default_factory=list, alias="user_ids")
    author: str
    quote: str
    category: Optional[str]
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
