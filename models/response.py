from typing import Union
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Enum

class BaseResponse(BaseModel):
    code: int = 200
    status: str

class UserResponse(BaseResponse):
    data: Optional[Union[dict, list]]

class UserResponsePagination(UserResponse):
    page: Optional[dict]

class AuthResponse(BaseResponse):
    data: Optional[Union[dict, list]]

class GeneralDataResponse(BaseResponse):
    data: Optional[Union[dict, list]]

class GeneralDataPaginateResponse(BaseResponse):
    data: Optional[Union[dict, list]]
    meta: Optional[Union[dict, list]]
