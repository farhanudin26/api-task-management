
from typing import Optional
from pydantic import BaseModel, Field

class CreateRole(BaseModel):
    role_id: str = Field(..., min_length=1, max_length=36)
    code: str = Field(..., min_length=1, max_length=36)
    level: int = Field(0)
    name: str = Field(..., min_length=1, max_length=126)
    description: str = Field(..., min_length=0, max_length=256)

class EditRole(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=36)
    level: int = Field(0)
    name: Optional[str] = Field(None, min_length=1, max_length=126)
    description: Optional[str] = Field(None, min_length=0, max_length=256)
    is_active: bool = Field(default=True)