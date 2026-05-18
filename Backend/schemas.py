from pydantic import BaseModel, EmailStr
from datetime import datetime


class RegisterSchema(BaseModel):

    username: str
    email: EmailStr
    password: str


# LOGIN SCHEMA
class LoginSchema(BaseModel):

    email: EmailStr
    password: str


# ROOM SCHEMA
class RoomSchema(BaseModel):

    name: str


# MESSAGE SCHEMA
class MessageSchema(BaseModel):

    content: str
    room_id: int


# RESPONSE MESSAGE SCHEMA
class MessageResponse(BaseModel):

    id: int
    content: str
    created_at: datetime

    user_id: int
    room_id: int

    class Config:
        from_attributes = True


class UserResponse(BaseModel):

    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True
class RoomSchema(BaseModel):

    name: str

    user_id: int
class InviteSchema(BaseModel):

    email:str
class ForgotSchema( BaseModel):
    email:str
class ResetSchema(
    BaseModel
):

    token:str

    new_password:str