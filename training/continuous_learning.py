import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3 as sqlcipher

class ContinuousLearningManager:
    def __init__(self, db_path: str = "user_interactions_encrypted.db"):
        self.db_path = db_path
        # self.db_key = os.environ.get('OVERSEER_DB_KEY')
        # if not self.db_key:
        #     raise RuntimeError('OVERSEER_DB_KEY environment variable not set!')
        self.init_database()

    def get_connection(self):
        conn = sqlcipher.connect(self.db_path)
        cursor = conn.cursor()
        # cursor.execute(f"PRAGMA key='{self.db_key}';")  # Removed for standard SQLite
        return conn, cursor

    def init_database(self):
        conn, cursor = self.get_connection()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_input TEXT,
                ai_response TEXT,
                user_feedback INTEGER,
                context TEXT,
                success BOOLEAN
            )
        ''')
        conn.commit()
        conn.close()

    def log_interaction(self, user_input: str, ai_response: str, context: Dict, success: bool = True, feedback: int = 0):
        conn, cursor = self.get_connection()
        cursor.execute('''
            INSERT INTO user_interactions 
            (user_input, ai_response, user_feedback, context, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_input, ai_response, feedback, json.dumps(context), success))
        conn.commit()
        conn.close()

    def get_training_data(self, min_feedback: int = 0) -> List[Dict]:
        conn, cursor = self.get_connection()
        cursor.execute('''
            SELECT user_input, ai_response, context 
            FROM user_interactions 
            WHERE user_feedback >= ? AND success = 1
            ORDER BY timestamp DESC
        ''', (min_feedback,))
        results = cursor.fetchall()
        conn.close()
        training_data = []
        for user_input, ai_response, context in results:
            training_data.append({
                'input': user_input,
                'output': ai_response,
                'context': json.loads(context)
            })
        return training_data

    def should_retrain(self, threshold: int = 1000) -> bool:
        conn, cursor = self.get_connection()
        cursor.execute('''
            SELECT COUNT(*) FROM user_interactions 
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        recent_interactions = cursor.fetchone()[0]
        conn.close()
        return recent_interactions >= threshold 