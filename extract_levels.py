import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import os

def load_pivot_points(symbol, interval, db_path='data/eurusd_trading.db'):
    """
    SQLiteデータベースからピボットポイントデータを読み込みます。

    Args:
        symbol (str): シンボル名
        interval (str): データの間隔（'daily' または 'weekly'）
        db_path (str): データベースのパス

    Returns:
        pd.DataFrame: 読み込まれたピボットポイントデータフレーム
    """
    try:
        conn = sqlite3.connect(db_path)
        query = f"""
        SELECT timestamp, Pivot, Support1, Resistance1, Support2, Resistance2
        FROM pivot_points
        WHERE symbol = '{symbol}' AND interval = '{interval}'
        ORDER BY timestamp ASC
        """
        df = pd.read_sql_query(query, conn, parse_dates=['timestamp'], index_col='timestamp')
        conn.close()
        return df
    except Exception as e:
        print(f"データベースからの読み込み中にエラーが発生しました: {e}")
        return pd.DataFrame()

def extract_levels(df, num_clusters=5):
    """
    高値と安値をクラスタリングし、サポート・レジスタンスラインを抽出します。

    Args:
        df (pd.DataFrame): ピボットポイントを含むデータフレーム
        num_clusters (int): クラスタ数

    Returns:
        list: 抽出された価格レベルのリスト
    """
    high_prices = df['Resistance1'].values.reshape(-1, 1)
    low_prices = df['Support1'].values.reshape(-1, 1)
    all_prices = np.vstack((high_prices, low_prices))

    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    kmeans.fit(all_prices)
    levels = sorted([cluster[0] for cluster in kmeans.cluster_centers_])
    return levels

def save_levels_to_db(levels, symbol, interval, db_path='data/eurusd_trading.db'):
    """
    抽出された価格レベルをSQLiteデータベースに保存します。

    Args:
        levels (list): 抽出された価格レベルのリスト
        symbol (str): シンボル名
        interval (str): データの間隔（'daily' または 'weekly'）
        db_path (str): データベースのパス
    """
    try:
        conn = sqlite3.connect(db_path)
        for level in levels:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO price_levels (symbol, interval, level)
                VALUES (?, ?, ?)
            ''', (symbol, interval, level))
        conn.commit()
        conn.close()
        print(f"{interval}データの価格レベルをデータベースに保存しました")
    except Exception as e:
        print(f"SQLiteへの保存中にエラーが発生しました: {e}")

def setup_price_levels_table(db_path='data/eurusd_trading.db'):
    """
    price_levels テーブルを作成します。

    Args:
        db_path (str): データベースのパス
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            interval TEXT,
            level REAL
        )
        ''')
        conn.commit()
        conn.close()
        print("price_levels テーブルを作成しました")
    except Exception as e:
        print(f"SQLiteへの接続中にエラーが発生しました: {e}")

def main():
    SYMBOL = 'EURUSD'
    INTERVALS = ['daily', 'weekly']
    db_path = 'data/eurusd_trading.db'
    
    # price_levels テーブルのセットアップ
    setup_price_levels_table(db_path)
    
    for interval in INTERVALS:
        df = load_pivot_points(SYMBOL, interval, db_path)
        if not df.empty:
            levels = extract_levels(df, num_clusters=5)
            save_levels_to_db(levels, SYMBOL, interval, db_path)
        else:
            print(f"{interval}データが存在しません")

if __name__ == "__main__":
    main()
