from pydantic import BaseModel, Field


class Checksum(BaseModel):
    md5: str = Field(min_length=32, max_length=32)
