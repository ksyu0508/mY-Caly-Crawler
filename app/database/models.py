from sqlalchemy import Column, Integer, String, DateTime, Boolean, PrimaryKeyConstraint, ForeignKey
from app.database.db import Base


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

class Image(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('post.id', ondelete='CASCADE'))
    link = Column(String, index=False)
    # organized = Column(Boolean, index=True)
    # contents = Column(String, index=True)


class Information(Base):
    __tablename__ = "information"

    post_id = Column(Integer, ForeignKey('post.id', ondelete='CASCADE'))
    tag = Column(String, index=True)
    type = Column(String, index=True)
    startAt = Column(DateTime, index=False)
    endAt = Column(DateTime, index=False)

    __table_args__ = (
        PrimaryKeyConstraint("post_id", "tag"),
    )
    
