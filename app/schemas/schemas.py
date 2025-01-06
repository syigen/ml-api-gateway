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


class AuthRequest(BaseModel):
    """
        Represents the user's login credentials.

        Attributes:
        - email (EmailStr): The user's email address.
        - password (str): The user's password.
    """
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """
        Represents the authenticated user's details.

        Attributes:
        - id (int): The user's ID.
        - email (EmailStr): The user's email address.
    """
    id: int
    email: EmailStr
