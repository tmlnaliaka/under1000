from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class UserRegister(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()


class UserLogin(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: float = Field(..., gt=0, le=1000)
    seller: str = Field(..., min_length=1, max_length=100)
    whatsapp: str = Field(..., min_length=10, max_length=20)
    location: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    image_url: Optional[str] = Field(None, max_length=500)
    inventory: int = Field(1, ge=0, le=10000)

    @field_validator("price")
    @classmethod
    def round_price(cls, v: float) -> float:
        return round(v, 2)

    @field_validator("whatsapp")
    @classmethod
    def validate_whatsapp(cls, v: str) -> str:
        digits = "".join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError("WhatsApp number too short")
        return digits


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, gt=0, le=1000)
    approved: Optional[bool] = None
    inventory: Optional[int] = Field(None, ge=0, le=10000)


class ProductOut(ProductBase):
    id: int
    approved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(1, ge=1, le=100)


class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductOut

    model_config = ConfigDict(from_attributes=True)


class CheckoutRequest(BaseModel):
    payment_method: str = Field("mock", pattern="^(mock|card|mpesa)$")
    discount_code: Optional[str] = Field(None, max_length=30)

    @field_validator("discount_code")
    @classmethod
    def upper_code(cls, v: Optional[str]) -> Optional[str]:
        return v.upper() if v else v


class OrderOut(BaseModel):
    id: int
    total: float
    tax: float
    discount_code: Optional[str]
    discount_amount: float
    status: str
    payment_method: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
