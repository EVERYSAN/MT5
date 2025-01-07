# scripts/add_data.py

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# SQLiteデータベースのパス
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'eurusd_trading.db')

def add_data():
    conn = sqlite3.connect(DB_PATH)
    df_existing = pd.read_sql_query("SELECT * FROM price_data WHERE interval = 'daily' ORDER BY timestamp ASC", conn, parse_dates=['timestamp'])
    conn.close()

    # 新しいデータを生成（例: 追加で200日分）
    start_date = df_existing['timestamp'].max() + timedelta(days=1)
    new_data = {
        'timestamp': [start_date + timedelta(days=i) for i in range(200)],
        'symbol': ['EURUSD'] * 200,
        'open': [1.200 + 0.001 * i for i in range(200)],
        'high': [1.205 + 0.001 * i for i in range(200)],
        'low': [1.195 + 0.001 * i for i in range(200)],
        'close': [1.200 + 0.001 * i for i in range(200)],
        'volume': [1000 + 10 * i for i in range(200)],
        'interval': ['daily'] * 200
    }
    df_new = pd.DataFrame(new_data)

    # データベースにデータを追加
    conn = sqlite3.connect(DB_PATH)
    df_new.to_sql('price_data', conn, if_exists='append', index=False)
    conn.close()

    print("新しいデータを追加しました。")

if __name__ == "__main__":
    add_data()
