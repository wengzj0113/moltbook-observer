from sqlalchemy.orm import Session
from database import SessionLocal, Post
from collector import translate_text
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_translate():
    db = SessionLocal()
    try:
        # Only translate the latest 20 posts to save time and API quota
        posts = db.query(Post).order_by(Post.created_at.desc()).limit(20).all()
        logger.info(f"Found {len(posts)} latest posts to check/translate...")
        
        count = 0
        for p in posts:
            # Check if translation is missing or same as original (assuming English original)
            # Or just force update for these 20
            if p.title:
                logger.info(f"Translating: {p.title[:30]}...")
                try:
                    # Translate Title
                    zh_title = translate_text(p.title, 'zh-CN')
                    if zh_title and zh_title != p.title:
                        p.title_zh = zh_title
                    
                    # Translate Content (if exists and not too long)
                    if p.content:
                        zh_content = translate_text(p.content, 'zh-CN')
                        if zh_content and zh_content != p.content:
                            p.content_zh = zh_content
                            
                    count += 1
                    # Sleep briefly to be nice to the API
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f"Error translating {p.id}: {e}")
            
        db.commit()
        logger.info(f"Translation update complete for {count} posts.")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    force_translate()
