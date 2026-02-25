from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./moltbook_zh.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def migrate_comments():
    with engine.connect() as conn:
        print("Migrating database for Comments...")
        try:
            # SQLite syntax for creating table if not exists
            sql = text("""
            CREATE TABLE IF NOT EXISTS comments (
                id VARCHAR PRIMARY KEY,
                content TEXT,
                content_zh TEXT,
                author_id VARCHAR,
                post_id VARCHAR,
                parent_id VARCHAR,
                upvotes INTEGER DEFAULT 0,
                created_at DATETIME,
                FOREIGN KEY(author_id) REFERENCES authors(id),
                FOREIGN KEY(post_id) REFERENCES posts(id),
                FOREIGN KEY(parent_id) REFERENCES comments(id)
            )
            """)
            conn.execute(sql)
            print("Created comments table.")
        except Exception as e:
            print(f"Error creating comments table: {e}")
        conn.commit()

if __name__ == "__main__":
    migrate_comments()
