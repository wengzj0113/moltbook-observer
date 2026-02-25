from sqlalchemy import create_engine, Column, String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    avatar_url = Column(String, nullable=True)
    karma = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    is_claimed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    last_active = Column(DateTime, nullable=True)

class Submolt(Base):
    __tablename__ = 'submolts'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    display_name = Column(String)

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(String, primary_key=True)
    title = Column(String)
    title_zh = Column(String, nullable=True)
    title_fr = Column(String, nullable=True)
    title_ja = Column(String, nullable=True)
    title_it = Column(String, nullable=True)
    title_ru = Column(String, nullable=True)
    title_ko = Column(String, nullable=True)
    title_es = Column(String, nullable=True)
    
    content = Column(Text)
    content_zh = Column(Text, nullable=True)
    content_fr = Column(Text, nullable=True)
    content_ja = Column(Text, nullable=True)
    content_it = Column(Text, nullable=True)
    content_ru = Column(Text, nullable=True)
    content_ko = Column(Text, nullable=True)
    content_es = Column(Text, nullable=True)
    
    type = Column(String)
    author_id = Column(String, ForeignKey('authors.id'))
    submolt_id = Column(String, ForeignKey('submolts.id'))
    
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    score = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    hot_score = Column(Integer, default=0)
    
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("Author", backref="posts")
    submolt = relationship("Submolt", backref="posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String, primary_key=True, index=True)
    content = Column(Text)
    content_zh = Column(Text, nullable=True) # Translated content
    
    author_id = Column(String, ForeignKey('authors.id'))
    post_id = Column(String, ForeignKey('posts.id'))
    parent_id = Column(String, ForeignKey('comments.id'), nullable=True)
    
    upvotes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("Author")
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

import os

# Database setup
# Use DATABASE_URL env var if available (for cloud deployment), otherwise fallback to local sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./moltbook_zh.db")

# Handle PostgreSQL URL format for SQLAlchemy (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
