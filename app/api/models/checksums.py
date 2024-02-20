from pydantic import BaseModel, Field


class Checksum(BaseModel):
    md5: str = Field(max_length=32)
