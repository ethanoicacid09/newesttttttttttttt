from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserWithOrders(UserResponse):
    orders: List["OrderResponse"] = []
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    stock_quantity: int = 0
    image_url: Optional[str] = None
    images: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    images: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    is_featured: bool
    rating: float
    review_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int

# Course Schemas
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    instructor: Optional[str] = None
    instructor_bio: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    duration_hours: Optional[float] = None
    level: Optional[str] = None
    total_videos: Optional[int] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    instructor: Optional[str] = None
    instructor_bio: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    duration_hours: Optional[float] = None
    level: Optional[str] = None
    total_videos: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

class CourseResponse(CourseBase):
    id: int
    is_active: bool
    is_featured: bool
    rating: float
    enrollment_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CourseListResponse(BaseModel):
    courses: List[CourseResponse]
    total: int
    page: int
    page_size: int

# Cart Schemas
class CartItemBase(BaseModel):
    product_id: Optional[int] = None
    course_id: Optional[int] = None
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    created_at: datetime
    product: Optional[ProductResponse] = None
    course: Optional[CourseResponse] = None
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float

# Order Schemas
class OrderItemBase(BaseModel):
    product_id: Optional[int] = None
    course_id: Optional[int] = None
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    total: float
    product: Optional[ProductResponse] = None
    course: Optional[CourseResponse] = None
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None
    payment_status: Optional[str] = None
    notes: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    user_id: int
    order_number: str
    status: OrderStatus
    subtotal: float
    tax: float
    shipping_cost: float
    total: float
    payment_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: UserResponse
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int

# Review Schemas
class ReviewBase(BaseModel):
    product_id: Optional[int] = None
    course_id: Optional[int] = None
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None
    is_approved: Optional[bool] = None

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    is_approved: bool
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True

# Contact Schemas
class ContactBase(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    is_resolved: Optional[bool] = None

class ContactResponse(ContactBase):
    id: int
    is_resolved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Enrollment Schemas
class EnrollmentBase(BaseModel):
    course_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentUpdate(BaseModel):
    progress: Optional[float] = None
    is_completed: Optional[bool] = None

class EnrollmentResponse(EnrollmentBase):
    id: int
    user_id: int
    progress: float
    is_completed: bool
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    course: Optional[CourseResponse] = None
    
    class Config:
        from_attributes = True

# Update forward references
UserWithOrders.model_rebuild()
