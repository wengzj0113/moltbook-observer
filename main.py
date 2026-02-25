from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_
from database import SessionLocal, Post, Author, Submolt, Comment, init_db
from collector import fetch_and_save_posts
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import os
import re
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Schemas
class AuthorBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    karma: int = 0
    model_config = ConfigDict(from_attributes=True)

class SubmoltBase(BaseModel):
    id: str
    name: str
    display_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PostResponse(BaseModel):
    id: str
    title: Optional[str] = None
    title_zh: Optional[str] = None
    title_fr: Optional[str] = None
    title_ja: Optional[str] = None
    title_it: Optional[str] = None
    title_ru: Optional[str] = None
    title_ko: Optional[str] = None
    title_es: Optional[str] = None
    
    content: Optional[str] = None
    content_zh: Optional[str] = None
    content_fr: Optional[str] = None
    content_ja: Optional[str] = None
    content_it: Optional[str] = None
    content_ru: Optional[str] = None
    content_ko: Optional[str] = None
    content_es: Optional[str] = None
    
    type: Optional[str] = None
    author: Optional[AuthorBase] = None
    submolt: Optional[SubmoltBase] = None
    upvotes: int = 0
    comment_count: int = 0
    score: int = 0
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Scheduler setup
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    init_db()
    
    logger.info("Starting scheduler...")
    # Run once immediately on startup but in background to avoid blocking
    try:
        scheduler.add_job(fetch_and_save_posts, 'date', run_date=datetime.now())
    except Exception as e:
        logger.error(f"Initial fetch scheduling failed: {e}")
        
    # Randomized interval: 15 seconds + jitter
    scheduler.add_job(fetch_and_save_posts, 'interval', seconds=15, jitter=5)
    scheduler.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down scheduler...")
    scheduler.shutdown()

app = FastAPI(title="Moltbook Observer", lifespan=lifespan)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CommentResponse(BaseModel):
    id: str
    content: str
    content_zh: Optional[str] = None
    author: AuthorBase
    upvotes: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# API Endpoints
@app.get("/api/posts", response_model=List[PostResponse])
def get_posts(skip: int = 0, limit: int = 100, sort: str = "new", db: Session = Depends(get_db)):
    query = db.query(Post).options(joinedload(Post.author), joinedload(Post.submolt))
    
    if sort == "new":
        query = query.order_by(desc(Post.created_at))
    elif sort == "top":
        query = query.order_by(desc(Post.score))
    elif sort == "discussed":
        query = query.order_by(desc(Post.comment_count))
    elif sort == "random" or sort == "shuffle":
        query = query.order_by(func.random())
        
    posts = query.offset(skip).limit(limit).all()
    return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post_detail(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).options(joinedload(Post.author), joinedload(Post.submolt)).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/api/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_post_comments(post_id: str, db: Session = Depends(get_db)):
    comments = db.query(Comment).options(joinedload(Comment.author)).filter(Comment.post_id == post_id).order_by(desc(Comment.created_at)).all()
    return comments

@app.get("/api/search", response_model=List[PostResponse])
def search_posts(q: str, limit: int = 20, db: Session = Depends(get_db)):
    search_term = f"%{q}%"
    posts = db.query(Post).options(joinedload(Post.author), joinedload(Post.submolt)).filter(
        or_(
            Post.title.ilike(search_term),
            Post.content.ilike(search_term),
            Post.title_zh.ilike(search_term),
            Post.content_zh.ilike(search_term),
            # Also search author name
            Post.author.has(Author.name.ilike(search_term))
        )
    ).order_by(desc(Post.created_at)).limit(limit).all()
    return posts

@app.get("/api/authors/{author_id}")
def get_author_profile(author_id: str, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    # Get recent posts
    posts = db.query(Post).options(joinedload(Post.author), joinedload(Post.submolt)).filter(Post.author_id == author_id).order_by(desc(Post.created_at)).limit(50).all()
    
    # Calculate stats
    post_count = db.query(Post).filter(Post.author_id == author_id).count()
    
    return {
        "author": author,
        "posts": posts,
        "stats": {
            "post_count": post_count,
            "karma": author.karma
        }
    }

@app.get("/api/trends")
def get_trends(db: Session = Depends(get_db)):
    # Analyze last 200 posts
    posts = db.query(Post).order_by(desc(Post.created_at)).limit(200).all()
    
    text_en = ""
    for p in posts:
        if p.title: text_en += p.title + " "
        if p.content: text_en += p.content + " "
        
    # Simple tokenization
    words = re.findall(r'\w+', text_en.lower())
    
    # Common stop words
    stop_words = {
        "the", "a", "an", "in", "to", "of", "and", "is", "it", "that", "for", "on", "with", "as", "this", "be", "are", "from", "at", "or", "by", "not", "but", "what", "all", "were", "we", "when", "your", "can", "said", "there", "use", "do", "how", "post", "deleted", "removed", "just", "have", "like", "so", "if", "my", "me", "about", "out", "up", "has", "was", "will", "they", "one", "some", "would", "get", "more", "who", "which", "time", "people", "don", "know", "think"
    }
    
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3 and not w.isdigit()]
    counter = Counter(filtered_words)
    
    return counter.most_common(10)

@app.get("/api/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    # Top Authors by Karma (All time)
    top_karma = db.query(Author).order_by(desc(Author.karma)).limit(100).all()
    
    # Most Vocal (Most posts in last 24h)
    one_day_ago = datetime.utcnow() - timedelta(hours=24)
    most_vocal = db.query(
        Author.name, 
        Author.id,
        func.count(Post.id).label('post_count')
    ).join(Post).filter(Post.created_at >= one_day_ago).group_by(Author.id).order_by(desc('post_count')).limit(100).all()
    
    # Viral Posts (Top score in last 48h)
    two_days_ago = datetime.utcnow() - timedelta(hours=48)
    viral_posts = db.query(Post).options(joinedload(Post.author)).filter(Post.created_at >= two_days_ago).order_by(desc(Post.score)).limit(100).all()

    return {
        "top_karma": top_karma,
        "most_vocal": [{"name": name, "id": id, "count": count} for name, id, count in most_vocal],
        "viral_posts": viral_posts
    }

@app.get("/api/activity")
def get_activity(db: Session = Depends(get_db)):
    # Activity over last 24 hours (grouped by hour)
    one_day_ago = datetime.utcnow() - timedelta(hours=24)
    
    # SQLite grouping by hour
    # Note: strftime syntax differs slightly between SQLite and PostgreSQL, using Python to aggregate for portability
    posts = db.query(Post.created_at).filter(Post.created_at >= one_day_ago).all()
    
    hourly_counts = Counter()
    for p in posts:
        hour_key = p.created_at.strftime("%H:00")
        hourly_counts[hour_key] += 1
        
    # Ensure all 24 hours are present (even with 0 counts)
    result = []
    now = datetime.utcnow()
    for i in range(24):
        t = now - timedelta(hours=i)
        key = t.strftime("%H:00")
        result.append({"time": key, "count": hourly_counts.get(key, 0)})
        
    return list(reversed(result))

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total_posts = db.query(Post).count()
    total_authors = db.query(Author).count()
    total_submolts = db.query(Submolt).count()
    total_comments = db.query(Comment).count()
    
    # Get top authors for sidebar
    top_authors = db.query(Author).order_by(desc(Author.karma)).limit(5).all()
    
    # Get popular submolts
    popular_submolts = db.query(
        Submolt.name, 
        func.count(Post.id).label('count')
    ).join(Post).group_by(Submolt.name).order_by(desc('count')).limit(5).all()
    
    # Get recent agents (newly active)
    recent_agents = db.query(Author).order_by(desc(Author.created_at)).limit(10).all()
    
    return {
        "total_posts": total_posts,
        "total_authors": total_authors,
        "total_submolts": total_submolts,
        "total_comments": total_comments,
        "top_authors": top_authors,
        "popular_submolts": [{"name": name, "count": count} for name, count in popular_submolts],
        "recent_agents": recent_agents
    }

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
