from pydantic import BaseModel, EmailStr


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
