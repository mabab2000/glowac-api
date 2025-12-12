"""Pydantic schemas for the Glowac API."""

from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class Banner(BaseModel):
    id: int
    highlight_tag: str
    title: str
    description: Optional[str] = None
    image_mime: Optional[str] = None
    image_preview_url: Optional[str] = None


__all__ = ["Banner"]


class Tus(BaseModel):
    id: int
    day: str
    hours: str
    status: str


__all__.append("Tus")


class Fact(BaseModel):
    id: int
    label: str
    number: int
    status: str


__all__.append("Fact")


class Why(BaseModel):
    id: int
    label: str
    value: str
    status: str


__all__.append("Why")


class Background(BaseModel):
    id: int
    paragraph: str


__all__.append("Background")


class CoreValue(BaseModel):
    id: int
    bullet_text: str


__all__.append("CoreValue")


class Gallery(BaseModel):
    id: int
    image_preview_url: Optional[str] = None


__all__.append("Gallery")


class CEO(BaseModel):
    id: int
    name: str
    title: str
    email: str
    image_url: Optional[str] = None
    image_mime: Optional[str] = None
    short_description: Optional[str] = None


__all__.append("CEO")


class Member(BaseModel):
    id: int
    name: str
    title: str
    email: str
    image_url: Optional[str] = None
    image_mime: Optional[str] = None
    short_description: Optional[str] = None


__all__.append("Member")


class MainService(BaseModel):
    id: int
    service_name: str


__all__.append("MainService")


class SubService(BaseModel):
    id: int
    main_service_id: int
    service_name: str
    description: Optional[str] = None


__all__.append("SubService")


class ServiceTest(BaseModel):
    id: int
    main_service_id: int
    sub_service_id: int
    test_name: str
    description: Optional[str] = None


__all__.append("ServiceTest")


class Message(BaseModel):
    id: int
    name: str
    email: str
    message: str
    created_at: datetime


__all__.append("Message")


class MessageResponse(BaseModel):
    message: str
    data: Message


__all__.append("MessageResponse")


class GeotechRequest(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    project_details: str
    created_at: datetime


__all__.append("GeotechRequest")
