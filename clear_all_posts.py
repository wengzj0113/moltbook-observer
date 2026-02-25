from database import SessionLocal, Post, Comment

def clear_all():
    db = SessionLocal()
    try:
        deleted_posts = db.query(Post).delete()
        deleted_comments = db.query(Comment).delete()
        db.commit()
        print(f"Deleted {deleted_posts} posts and {deleted_comments} comments.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_all()