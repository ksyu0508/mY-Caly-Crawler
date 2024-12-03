from app.database.db import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship


class Post(Base):
    __tablename__ = "post"  # Table name

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    contents = Column(String, index=False)
    college = Column(String, index=True)
    original_link = Column(String, index=False)
    createdAt = Column(DateTime, index=True)
    organized = Column(Boolean, index=True)
    # image_id = Column(Integer, ForeignKey('image.id'))
    
    information = relationship("Information", back_populates="post")  
    image = relationship("Image", back_populates="post") 

class Image(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('post.id', ondelete='CASCADE'))
    img_contents = Column(String, index=False)
    link = Column(String, index=False)
    # organized = Column(Boolean, index=True)
    # contents = Column(String, index=True)

    post = relationship("Post", back_populates="image")

class Information(Base):
    __tablename__ = "information"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('post.id', ondelete='CASCADE'), index=True)
    tags = Column(ARRAY(String), index=True)
    type = Column(String, index=True)
    startAt = Column(DateTime, index=False)
    endAt = Column(DateTime, index=False)

    post = relationship("Post", back_populates="information")
    # tag = Column(String, index=True)
    # __table_args__ = (
    #     PrimaryKeyConstraint("post_id", "tag"),
    # )
    
