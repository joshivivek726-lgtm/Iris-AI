"""
Database module for Iris AI
Handles SQLite setup and conversation storage
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """SQLite database handler for Iris AI"""
    
    def __init__(self, db_path: str = "./iris.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection = None
        self.init_db()
    
    def connect(self) -> sqlite3.Connection:
        """Create database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def init_db(self):
        """Initialize database tables"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            ''')
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tokens_used INTEGER,
                    processing_time_ms REAL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
                )
            ''')
            
            # Create user preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    preferences TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_id ON messages(conversation_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON conversations(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def create_conversation(self, conversation_id: str, user_id: str, metadata: Optional[Dict] = None) -> bool:
        """Create a new conversation"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO conversations (conversation_id, user_id, metadata)
                VALUES (?, ?, ?)
            ''', (conversation_id, user_id, json.dumps(metadata) if metadata else None))
            self.connection.commit()
            logger.info(f"Created conversation: {conversation_id}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Conversation already exists: {conversation_id}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Failed to create conversation: {e}")
            raise
    
    def save_message(self, conversation_id: str, user_id: str, role: str, content: str, 
                    tokens_used: Optional[int] = None, processing_time_ms: Optional[float] = None) -> bool:
        """Save a message to a conversation"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO messages (conversation_id, user_id, role, content, tokens_used, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (conversation_id, user_id, role, content, tokens_used, processing_time_ms))
            
            # Update conversation updated_at and message_count
            cursor.execute('''
                UPDATE conversations 
                SET updated_at = CURRENT_TIMESTAMP, 
                    message_count = message_count + 1
                WHERE conversation_id = ?
            ''', (conversation_id,))
            
            self.connection.commit()
            logger.info(f"Saved {role} message to {conversation_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to save message: {e}")
            raise
    
    def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT role, content, timestamp
                FROM (
                    SELECT role, content, timestamp, rowid AS message_rowid
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY timestamp DESC, rowid DESC
                    LIMIT ?
                )
                ORDER BY timestamp ASC, message_rowid ASC
            ''', (conversation_id, limit))
            
            rows = cursor.fetchall()
            messages = [dict(row) for row in rows]
            logger.info(f"Retrieved {len(messages)} messages from {conversation_id}")
            return messages
        except sqlite3.Error as e:
            logger.error(f"Failed to get conversation history: {e}")
            raise
    
    def get_recent_conversations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent conversations for a user"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT conversation_id, user_id, created_at, updated_at, message_count
                FROM conversations
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            conversations = [dict(row) for row in rows]
            return conversations
        except sqlite3.Error as e:
            logger.error(f"Failed to get recent conversations: {e}")
            raise
    
    def save_user_preference(self, user_id: str, preferences: Dict) -> bool:
        """Save user preferences"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (user_id, preferences, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, json.dumps(preferences)))
            self.connection.commit()
            logger.info(f"Saved preferences for user: {user_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to save preferences: {e}")
            raise
    
    def get_user_preference(self, user_id: str) -> Optional[Dict]:
        """Get user preferences"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT preferences FROM user_preferences WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row and row[0]:
                return json.loads(row[0])
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get preferences: {e}")
            raise
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and its messages"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
            cursor.execute('DELETE FROM conversations WHERE conversation_id = ?', (conversation_id,))
            self.connection.commit()
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to delete conversation: {e}")
            raise
    
    def get_db_stats(self) -> Dict:
        """Get database statistics"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT COUNT(*) FROM conversations')
            conversation_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM messages')
            message_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM user_preferences')
            user_count = cursor.fetchone()[0]
            
            return {
                "conversations": conversation_count,
                "messages": message_count,
                "users": user_count
            }
        except sqlite3.Error as e:
            logger.error(f"Failed to get stats: {e}")
            raise


# Global database instance
_db_instance: Optional[Database] = None


def get_database(db_path: str = "./iris.db") -> Database:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance


def init_database(db_path: str = "./iris.db") -> Database:
    """Initialize database"""
    global _db_instance
    _db_instance = Database(db_path)
    return _db_instance
