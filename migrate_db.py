from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./moltbook_zh.db")
# Handle PostgreSQL URL format for SQLAlchemy (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

new_columns = [
    "title_fr", "content_fr",
    "title_ja", "content_ja",
    "title_it", "content_it",
    "title_ru", "content_ru",
    "title_ko", "content_ko",
    "title_es", "content_es"
]

def migrate():
    with engine.connect() as conn:
        print("Migrating database...")
        for col in new_columns:
            col_type = "TEXT" if "content" in col else "VARCHAR"
            try:
                # SQLite ALTER TABLE ADD COLUMN
                sql = text(f"ALTER TABLE posts ADD COLUMN {col} {col_type}")
                conn.execute(sql)
                print(f"Added column: {col}")
            except Exception as e:
                if "duplicate column name" in str(e):
                    print(f"Column {col} already exists, skipping.")
                else:
                    print(f"Error adding {col}: {e}")
        conn.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate()
