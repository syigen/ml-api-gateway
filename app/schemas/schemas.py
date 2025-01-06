from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr

class LoginResponse(BaseModel):
    email: EmailStr
    message: str