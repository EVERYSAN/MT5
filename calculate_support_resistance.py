# scripts/calculate_support_resistance.py

import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import os
from datetime import datetime, timedelta


# SQLiteデータベースのパス
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'eurusd_trading.db')

def calculate_support_resistance():
    # データの取得
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT timestamp, high, low
    FROM price_data
    WHERE interval = 'daily'
    ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, parse_dates=['timestamp'])
    conn.close()
    
    # 高値と安値のクラスタリング
    highs = df['high'].values.reshape(-1, 1)
    lows = df['low'].values.reshape(-1, 1)
    
    # K-meansクラスタリングでサポートとレジスタンスラインを特定
    kmeans_high = KMeans(n_clusters=5, random_state=0).fit(highs)
    kmeans_low = KMeans(n_clusters=5, random_state=0).fit(lows)
    
    # 各クラスタの中心値をサポート・レジスタンスラインとする
    resistance_levels = sorted(kmeans_high.cluster_centers_.flatten(), reverse=True)
    support_levels = sorted(kmeans_low.cluster_centers_.flatten())
    

    
    # サポート・レジスタンスラインの保存
    support1 = support_levels[0]
    resistance1 = resistance_levels[0]
    
    # データベースに保存
    conn = sqlite3.connect(DB_PATH)
    insert_query = """
    INSERT INTO price_levels (timestamp, level, type, interval)
    VALUES (?, ?, ?, ?)
    """
    latest_timestamp = df['timestamp'].max()
    
    # ISO形式の文字列に変換
    latest_timestamp_str = latest_timestamp.isoformat()
    
    conn.execute(insert_query, (latest_timestamp_str, support1, 'Support1', 'daily'))
    conn.execute(insert_query, (latest_timestamp_str, resistance1, 'Resistance1', 'daily'))
    conn.commit()
    conn.close()
    
    print(f"サポートライン: {support1}, レジスタンスライン: {resistance1}")

if __name__ == "__main__":
    calculate_support_resistance()
