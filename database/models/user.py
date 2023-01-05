from datetime import datetime
from typing import List

from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr

from database.models.common import PyObjectId


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(...)
    email: EmailStr = Field(...)
    phone_number: str = Field(...)
    quotes: List[PyObjectId] = Field(default_factory=list, alias="quotes")
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserCreate(BaseModel):
    username: str
    email: str
    phone_number: str
