from database import SessionLocal, Post, engine
import os

def check_data():
    print(f"Current working directory: {os.getcwd()}")
    print(f"Database URL: {engine.url}")
    db = SessionLocal()
    try:
        count = db.query(Post).count()
        print(f"Total posts in DB: {count}")
        
        posts = db.query(Post).all()
        for p in posts:
            print(f"ID: {p.id}, Title: {p.title[:20]}, Created: {p.created_at}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()