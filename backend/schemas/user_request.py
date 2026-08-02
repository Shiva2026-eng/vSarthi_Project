from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRequestModel(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    model_config = {
        "from_attributes": True
    }

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name should contain only letters and spaces.")
        return value.strip()