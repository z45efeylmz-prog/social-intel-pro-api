import os
import sqlite3
import datetime
from typing import Dict, Any, List, Optional

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "social_intel.db")

class Database:
    """Thread-safe SQLite storage engine for social intelligence data."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Creators table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS creators (
                    username TEXT PRIMARY KEY,
                    platform TEXT,
                    followers INTEGER,
                    following INTEGER,
                    posts INTEGER,
                    er_pct REAL,
                    authenticity_score INTEGER,
                    risk_level TEXT,
                    growth_status TEXT,
                    recommendation TEXT,
                    updated_at TEXT
                )
            """)
            # 2. Trending sounds table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trending_sounds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    author TEXT,
                    video_count INTEGER,
                    velocity_pct REAL,
                    is_breakout INTEGER,
                    audio_url TEXT,
                    recorded_at TEXT
                )
            """)
            # 3. Trending hashtags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trending_hashtags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag TEXT,
                    views_24h INTEGER,
                    growth_rate_pct REAL,
                    niche TEXT,
                    recorded_at TEXT
                )
            """)
            conn.commit()

    def save_creator(self, data: Dict[str, Any]):
        m = data["metrics"]
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO creators 
                (username, platform, followers, following, posts, er_pct, authenticity_score, risk_level, growth_status, recommendation, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["username"],
                data["platform"],
                m.followers if hasattr(m, 'followers') else m['followers'],
                m.following if hasattr(m, 'following') else m['following'],
                m.total_posts if hasattr(m, 'total_posts') else m['total_posts'],
                m.engagement_rate_pct if hasattr(m, 'engagement_rate_pct') else m['engagement_rate_pct'],
                data["authenticity_score"],
                data["risk_level"],
                data["growth_status"],
                data["commercial_recommendation"],
                now
            ))
            conn.commit()

    def get_creator(self, username: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM creators WHERE username = ?", (username.lower(),))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def save_trends(self, sounds: List[Any], tags: List[Any]):
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for s in sounds:
                title = s.title if hasattr(s, 'title') else s['title']
                author = s.author if hasattr(s, 'author') else s['author']
                vc = s.video_count if hasattr(s, 'video_count') else s['video_count']
                vel = s.velocity_24h_pct if hasattr(s, 'velocity_24h_pct') else s['velocity_24h_pct']
                brk = 1 if (s.is_breakout if hasattr(s, 'is_breakout') else s['is_breakout']) else 0
                url = s.audio_url if hasattr(s, 'audio_url') else s.get('audio_url')
                cursor.execute("""
                    INSERT INTO trending_sounds (title, author, video_count, velocity_pct, is_breakout, audio_url, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (title, author, vc, vel, brk, url, now))

            for t in tags:
                tag = t.tag if hasattr(t, 'tag') else t['tag']
                views = t.views_24h if hasattr(t, 'views_24h') else t['views_24h']
                gr = t.growth_rate_pct if hasattr(t, 'growth_rate_pct') else t['growth_rate_pct']
                niche = t.niche if hasattr(t, 'niche') else t['niche']
                cursor.execute("""
                    INSERT INTO trending_hashtags (tag, views_24h, growth_rate_pct, niche, recorded_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (tag, views, gr, niche, now))
            conn.commit()

    def get_recent_sounds(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trending_sounds ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

db = Database()
