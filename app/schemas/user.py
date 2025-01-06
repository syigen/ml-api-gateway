from pydantic import BaseModel, EmailStr, constr, field_validator

class UserCreate(BaseModel):
    """
       Represents a user registration request.

       Attributes:
           email (EmailStr): The email address of the user.
           password (constr(min_length=8)): The password of the user.

       Methods:
           validate_password(cls, password):
               Validates the password by checking that it contains at least one digit,
               one uppercase letter, and one lowercase letter.

       Raises:
           ValueError: If the password does not meet the validation criteria.
    """
    email: EmailStr
    password: constr(min_length=8)

    @field_validator('password')
    def validate_password(cls, password):
        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in password):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in password):
            raise ValueError('Password must contain at least one lowercase letter')
        return password

class RegisterResponse(BaseModel):
    email: EmailStr
    message: str