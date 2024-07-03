from pydantic import BaseModel
from typing import Optional

class UserInput(BaseModel):
    message: str

class StakeholderBase(BaseModel):
    name: Optional[str]
    headline: Optional[str]
    summary: Optional[str]
    photo: Optional[str]
    source: Optional[str]
    source_id: Optional[str]
    series: Optional[int]

class Stakeholder(StakeholderBase):
    stakeholder_id: int

    class Config:
        orm_mode: True

class RelationshipBase(BaseModel):
    subject: int
    predicate: str
    object: int

class Relationship(RelationshipBase):
    id: int

    class Config:
        orm_mode: True

# class ItemBase(BaseModel):
#     title: str
#     description: str | None = None


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True


# class UserBase(BaseModel):
#     email: str


# class UserCreate(UserBase):
#     password: str


# class User(UserBase):
#     id: int
#     is_active: bool
#     items: list[Item] = []

#     class Config:
#         orm_mode = True