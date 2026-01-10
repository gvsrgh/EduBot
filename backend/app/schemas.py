from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Chat Schemas
class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"


class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    chat_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: str
    chat_id: str
    human: str
    bot: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatWithMessages(BaseModel):
    id: str
    title: str
    updated_at: datetime
    messages: list[MessageResponse]
    
    class Config:
        from_attributes = True


class ChatRename(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


# Settings Schemas
class ProviderUpdate(BaseModel):
    ai_provider: str = Field(..., pattern="^(openai|gemini|ollama|auto)$")


class ProviderResponse(BaseModel):
    ai_provider: str
    available_providers: dict[str, bool]


class SettingsResponse(BaseModel):
    id: int
    ai_provider: str
    deny_words: str
    max_tokens: int
    temperature: str
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    ai_provider: Optional[str] = Field(None, pattern="^(openai|gemini|ollama|auto)$")
    deny_words: Optional[str] = None
    max_tokens: Optional[int] = Field(None, ge=100, le=4000)
    temperature: Optional[str] = Field(None, pattern=r"^[0-1](\.[0-9]+)?$")
