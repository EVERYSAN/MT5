# scripts/setup_database.py

import sqlite3
import os

def setup_database(db_path='data/eurusd_trading.db'):
    """
    SQLiteデータベースと必要なテーブルを作成します。
    
    Args:
        db_path (str): データベースのパス
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 既存のテーブルを削除（スキーマ変更のため）
    cursor.execute('DROP TABLE IF EXISTS price_data')
    cursor.execute('DROP TABLE IF EXISTS pivot_points')
    cursor.execute('DROP TABLE IF EXISTS price_levels')
    cursor.execute('DROP TABLE IF EXISTS combined_price_levels')
    
    # price_dataテーブルの作成（複合主キー）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_data (
        timestamp TEXT,
        symbol TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        interval TEXT,
        PRIMARY KEY (timestamp, interval)
    )
    ''')
    
    # pivot_pointsテーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pivot_points (
        timestamp TEXT,
        Pivot REAL,
        Support1 REAL,
        Resistance1 REAL,
        Support2 REAL,
        Resistance2 REAL,
        symbol TEXT,
        interval TEXT,
        PRIMARY KEY (timestamp, interval)
    )
    ''')
    
    # price_levelsテーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        symbol TEXT,
        interval TEXT,
        level REAL,
        type TEXT,
        UNIQUE(timestamp, symbol, interval, level, type)
    )
    ''')
    
    # combined_price_levelsテーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS combined_price_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        level REAL
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database setup completed: {db_path}")

if __name__ == "__main__":
    setup_database()
