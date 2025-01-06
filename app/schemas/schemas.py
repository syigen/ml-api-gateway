from pydantic import BaseModel, EmailStr, constr

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    id: int
    email: EmailStr
    api_key: str

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$")

class UserResponse(BaseModel):
    id: int
    email: str

class UserLogin(BaseModel):
    email: EmailStr

class LoginResponse(BaseModel):
    email: EmailStr
    message: str