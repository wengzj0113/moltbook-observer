import requests
from sqlalchemy.orm import Session
from database import SessionLocal, Author, Submolt, Post, Comment, init_db
from datetime import datetime
from deep_translator import GoogleTranslator
import logging
import time
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def translate_text(text, target_lang='zh-CN'):
    if not text:
        return None
    
    # Optimization: Only translate to Chinese for now to ensure speed and stability
    # Expanding to all languages (7 langs * 2 fields * 20 posts = 280 requests) would block the loop too long
    if target_lang != 'zh-CN':
        return text

    try:
        # Increase timeout and add retry logic for cloud environment
        # Limit text length to avoid timeouts/errors with free APIs
        if len(text) > 4500:
            text = text[:4500]
        
        # Use a more robust call or just accept that free translation might fail in cloud
        # due to IP rate limits. In cloud, we might want to skip translation if it fails quickly
        # to avoid blocking the whole sync process.
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        logger.warning(f"Translation error ({target_lang}): {e}")
        return text # Fallback to original

def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Handle format: 2026-01-30T05:39:05.821Z
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        return None

def cleanup_database(db: Session):
    """
    Smart Pruning Strategy:
    1. Keep Top 100 All-Time High Score Posts (Hall of Fame)
    2. Keep Latest 200 Posts (Real-time Feed)
    3. Delete everything else
    """
    try:
        # Get IDs of Top 100 Posts
        top_100_ids = [r[0] for r in db.query(Post.id).order_by(Post.score.desc()).limit(100).all()]
        
        # Get IDs of Latest 200 Posts
        latest_200_ids = [r[0] for r in db.query(Post.id).order_by(Post.created_at.desc()).limit(200).all()]
        
        # Combine Whitelist
        whitelist_ids = set(top_100_ids + latest_200_ids)
        
        if not whitelist_ids:
            return

        # Delete posts not in whitelist
        # Note: In SQLite, DELETE with IN clause on large set might be slow, but for hundreds it's fine.
        # SQLAlchemy syntax for delete
        deleted_count = db.query(Post).filter(Post.id.notin_(whitelist_ids)).delete(synchronize_session=False)
        
        # Also clean up orphaned comments (if cascade delete isn't set up on DB level)
        # Assuming we should clean comments whose post_id is not in whitelist
        deleted_comments = db.query(Comment).filter(Comment.post_id.notin_(whitelist_ids)).delete(synchronize_session=False)
        
        db.commit()
        if deleted_count > 0:
            logger.info(f"Database Cleanup: Removed {deleted_count} old posts and {deleted_comments} comments. Kept {len(whitelist_ids)} active posts.")
            
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        db.rollback()

def fetch_and_save_posts():
    db: Session = SessionLocal()
    try:
        url_primary = "https://www.moltbook.com/api/v1/posts?sort=new"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.moltbook.com/"
        }

        def try_fetch():
            candidates = [
                f"{url_primary}",
                "https://www.moltbook.com/api/v1/posts?limit=100&sort=new",
                "https://www.moltbook.com/api/v1/posts",
                f"https://www.moltbook.com/api/v1/posts?_t={int(time.time())}",
                "https://www.moltbook.com/api/v1/posts?filter=new"
            ]
            
            # Log environment context to help debug cloud issues
            logger.info(f"Collector running. Env: {os.getenv('RENDER', 'Local')}. DB URL: {os.getenv('DATABASE_URL', 'default')}")
            
            for u in candidates:
                try:
                    logger.info(f"Fetching data from {u}...")
                    r = requests.get(u, headers=headers, timeout=15) # Increased timeout for cloud
                    if r.status_code != 200:
                        logger.warning(f"Failed to fetch from {u}: Status {r.status_code}")
                        continue
                    d = r.json()
                    ps = d.get("posts", [])
                    if ps:
                        return ps
                except Exception as e:
                    logger.warning(f"Exception fetching from {u}: {e}")
                    continue
            
            # Fallback logic...
            fallback_path = os.path.join(os.path.dirname(__file__), "api_response_posts.json")
            if os.path.exists(fallback_path):
                try:
                    with open(fallback_path, "r", encoding="utf-8") as f:
                        d = json.load(f)
                        ps = d.get("posts", [])
                        if ps:
                            logger.warning("Using cached api_response_posts.json as fallback")
                            return ps, True
                except Exception:
                    pass
            return [], False

        posts, is_offline = try_fetch()
        if not posts:
            logger.error("Failed to fetch posts from all sources")
            return
        logger.info(f"Fetched {len(posts)} posts. Mode: {'OFFLINE (No Translate)' if is_offline else 'ONLINE'}. Saving to database...")
        
        new_posts_count = 0
        updated_posts_count = 0
        
        # Local cache to handle duplicate authors/submolts in the same batch
        # when autoflush is False (or to save queries)
        # We also need to query existing ones first to populate this cache
        
        for p in posts:
            # 1. Upsert Author
            author_data = p.get("author", {})
            if not author_data:
                continue
            
            author_id = author_data.get("id")
            # Check DB or Session
            author = db.query(Author).filter(Author.id == author_id).first()
            if not author:
                # Check if we already added it in this session (but not flushed)
                # Since autoflush=False, query won't find it.
                # We can check db.new
                author = next((x for x in db.new if isinstance(x, Author) and x.id == author_id), None)
                
            if not author:
                author = Author(id=author_id)
                db.add(author)
            
            author.name = author_data.get("name")
            author.description = author_data.get("description")
            author.avatar_url = author_data.get("avatarUrl")
            author.karma = author_data.get("karma", 0)
            author.follower_count = author_data.get("followerCount", 0)
            author.following_count = author_data.get("followingCount", 0)
            author.is_claimed = author_data.get("isClaimed", False)
            author.is_active = author_data.get("isActive", True)
            author.created_at = parse_date(author_data.get("createdAt"))
            author.last_active = parse_date(author_data.get("lastActive"))
            
            # 2. Upsert Submolt
            submolt_data = p.get("submolt", {})
            if submolt_data:
                submolt_id = submolt_data.get("id")
                submolt = db.query(Submolt).filter(Submolt.id == submolt_id).first()
                if not submolt:
                    submolt = next((x for x in db.new if isinstance(x, Submolt) and x.id == submolt_id), None)
                    
                if not submolt:
                    submolt = Submolt(id=submolt_id)
                    db.add(submolt)
                submolt.name = submolt_data.get("name")
                submolt.display_name = submolt_data.get("display_name")
            
            # 3. Upsert Post
            post_id = p.get("id")
            post = db.query(Post).filter(Post.id == post_id).first()
            # Posts are unique in the feed usually, but good to be safe
            if not post:
                 post = next((x for x in db.new if isinstance(x, Post) and x.id == post_id), None)

            if not post:
                post = Post(id=post_id)
                db.add(post)
                new_posts_count += 1
            else:
                updated_posts_count += 1
                
            post.title = p.get("title")
            # Translate if new or title changed (simplified: just check if title_zh is empty)
            if post.title and not post.title_zh:
                if is_offline:
                    post.title_zh = post.title
                else:
                    post.title_zh = translate_text(post.title, 'zh-CN')
                    post.title_fr = translate_text(post.title, 'fr')
                    post.title_ja = translate_text(post.title, 'ja')
                    post.title_it = translate_text(post.title, 'it')
                    post.title_ru = translate_text(post.title, 'ru')
                    post.title_ko = translate_text(post.title, 'ko')
                    post.title_es = translate_text(post.title, 'es')
                
            post.content = p.get("content")
            if post.content and not post.content_zh:
                 if is_offline:
                     post.content_zh = post.content
                 else:
                     post.content_zh = translate_text(post.content, 'zh-CN')
                     post.content_fr = translate_text(post.content, 'fr')
                     post.content_ja = translate_text(post.content, 'ja')
                     post.content_it = translate_text(post.content, 'it')
                     post.content_ru = translate_text(post.content, 'ru')
                     post.content_ko = translate_text(post.content, 'ko')
                     post.content_es = translate_text(post.content, 'es')

            post.type = p.get("type")
            post.author_id = author.id
            post.submolt_id = submolt_data.get("id") if submolt_data else None
            post.upvotes = p.get("upvotes", 0)
            post.downvotes = p.get("downvotes", 0)
            post.score = p.get("score", 0)
            post.comment_count = p.get("comment_count", 0)
            post.hot_score = p.get("hot_score", 0)
            post.is_pinned = p.get("is_pinned", False)
            post.is_locked = p.get("is_locked", False)
            post.is_deleted = p.get("is_deleted", False)
            post.created_at = parse_date(p.get("created_at"))
            post.updated_at = parse_date(p.get("updated_at"))
            
            # 4. Upsert Comments (if any)
            comments_data = p.get("comments", [])
            if comments_data:
                for c in comments_data:
                    # Upsert Comment Author first
                    c_author_data = c.get("author", {})
                    if not c_author_data:
                        continue
                        
                    c_author_id = c_author_data.get("id")
                    c_author = db.query(Author).filter(Author.id == c_author_id).first()
                    if not c_author:
                        c_author = next((x for x in db.new if isinstance(x, Author) and x.id == c_author_id), None)
                    if not c_author:
                        c_author = Author(id=c_author_id)
                        db.add(c_author)
                    
                    c_author.name = c_author_data.get("name")
                    c_author.avatar_url = c_author_data.get("avatarUrl")
                    c_author.karma = c_author_data.get("karma", 0)
                    
                    # Upsert Comment
                    comment_id = c.get("id")
                    comment = db.query(Comment).filter(Comment.id == comment_id).first()
                    if not comment:
                        comment = next((x for x in db.new if isinstance(x, Comment) and x.id == comment_id), None)
                        
                    if not comment:
                        comment = Comment(id=comment_id)
                        db.add(comment)
                        
                    comment.content = c.get("content")
                    # Translate Comment Content (Simplified: Only Chinese)
                    if comment.content and not comment.content_zh:
                        if is_offline:
                            comment.content_zh = comment.content
                        else:
                            comment.content_zh = translate_text(comment.content, 'zh-CN')
                        
                    comment.author_id = c_author_id
                    comment.post_id = post_id
                    comment.upvotes = c.get("upvotes", 0)
                    comment.created_at = parse_date(c.get("createdAt"))
            
        db.commit()
        logger.info(f"Sync complete. New: {new_posts_count}, Updated: {updated_posts_count}")
        
        # Trigger Cleanup
        cleanup_database(db)
        
    except Exception as e:
        logger.error(f"Error during sync: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    try:
        # Check if database file exists before init to prevent overwrite or permission issues
        # Or just let init_db handle it (it uses create_all which is safe)
        init_db()
        logger.info("Database initialized.")
        fetch_and_save_posts()
    except Exception as e:
        logger.error(f"Collector main execution failed: {e}")
