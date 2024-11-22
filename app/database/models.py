from sqlalchemy import Column, Integer, Strings, Datetime
from app.database import Base

# class Queue(Base):
#     '''
#     unorganized documents are saved in queue, not posts
#     '''
#     __tablename__ = "queue"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     contents = Column(String, index=True)

class Post(Base):
    __tablename__ = "post"  # Table name

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    contents = Column(String, index=True)
    original_link = Column(String, index=False)
    organized = Column()
    createdAt = Column()
