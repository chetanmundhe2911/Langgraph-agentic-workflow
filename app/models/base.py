"""
Base model and helpers for all MongoDB collection schemas.
Compatible with pymongo dicts and Pydantic validation.
"""
from typing import Optional, Any, List, Dict
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field


class MongoModel(BaseModel):
    """Base model for all MongoDB documents."""
    id: Optional[str] = Field(None, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
        }

    @classmethod
    def from_mongo(cls, doc: Optional[dict]):
        if doc is None:
            return None
        doc = dict(doc)
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        for key, val in list(doc.items()):
            if hasattr(val, "__str__") and type(val).__name__ == "ObjectId":
                doc[key] = str(val)
        return cls(**doc)

    def to_mongo(self, include_none: bool = False) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=not include_none)
        data.pop("_id", None)
        return data


class TimestampMixin(MongoModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Common enums reused across multiple collections
# ---------------------------------------------------------------------------

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    completed = "completed"


class PlatformEnum(str, Enum):
    in_person = "in_person"
    phone = "phone"
    video_call = "video_call"
    web = "web"
    mobile = "mobile"
    ai_facilitated = "ai_facilitated"


class FlagType(str, Enum):
    none = "none"
    green_flag = "green_flag"
    yellow_flag = "yellow_flag"
    red_flag = "red_flag"
