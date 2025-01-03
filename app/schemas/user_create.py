from pydantic import BaseModel, EmailStr, constr
from pydantic.v1 import validator


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

    #ValidationNotCompleted
    @validator('password')
    def validate_password(self, password):
        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in password):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in password):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char in '!@#$%^&*()_+' for char in password):
            raise ValueError('Password must contain at least one special character')
        return password

class RegisterResponse(BaseModel):
    email: EmailStr
    message: str