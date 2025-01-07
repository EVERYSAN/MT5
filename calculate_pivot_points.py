# scripts/calculate_pivot_points.py

import sqlite3
import pandas as pd
import os
import logging

# ログディレクトリとファイル名を設定
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'pivot_calculation.log')

# ログディレクトリが存在しない場合は作成
os.makedirs(LOG_DIR, exist_ok=True)

# ログの設定
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# SQLiteデータベースのパス
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'eurusd_trading.db')

def fetch_price_data(interval):
    """
    データベースから指定した間隔の価格データを取得します。
    
    Args:
        interval (str): データの間隔（'daily' または 'weekly'）
    
    Returns:
        pd.DataFrame: 価格データ
    """
    conn = sqlite3.connect(DB_PATH)
    query = f"""
    SELECT timestamp, open, high, low, close
    FROM price_data
    WHERE interval = '{interval}'
    ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, parse_dates=['timestamp'])
    conn.close()
    return df

def calculate_pivot_points(df):
    """
    ピボットポイント、サポートライン、レジスタンスラインを計算します。
    
    Args:
        df (pd.DataFrame): 価格データ
    
    Returns:
        pd.DataFrame: ピボットポイントデータ
    """
    pivot_points = []
    for index, row in df.iterrows():
        pivot = (row['high'] + row['low'] + row['close']) / 3
        support1 = (2 * pivot) - row['high']
        resistance1 = (2 * pivot) - row['low']
        support2 = pivot - (row['high'] - row['low'])
        resistance2 = pivot + (row['high'] - row['low'])
        pivot_points.append({
            'timestamp': row['timestamp'],
            'Pivot': pivot,
            'Support1': support1,
            'Resistance1': resistance1,
            'Support2': support2,
            'Resistance2': resistance2
        })
    return pd.DataFrame(pivot_points)

def save_pivot_points(df_pivot, interval):
    """
    計算したピボットポイントをデータベースに保存します。
    
    Args:
        df_pivot (pd.DataFrame): ピボットポイントデータ
        interval (str): データの間隔（'daily' または 'weekly'）
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for _, row in df_pivot.iterrows():
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO pivot_points
                (timestamp, Pivot, Support1, Resistance1, Support2, Resistance2, symbol, interval)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                row['Pivot'],
                row['Support1'],
                row['Resistance1'],
                row['Support2'],
                row['Resistance2'],
                'EURUSD',
                interval
            ))
        except Exception as e:
            logging.error(f"Error inserting pivot points for {row['timestamp']}: {e}")
    
    conn.commit()
    conn.close()
    logging.info(f"{interval}ピボットポイントの計算と保存が完了しました")

def main():
    intervals = ['daily', 'weekly']
    for interval in intervals:
        logging.info(f"{interval}ピボットポイントの計算を開始します")
        df_price = fetch_price_data(interval)
        if df_price.empty:
            logging.warning(f"{interval}データが存在しません")
            continue
        df_pivot = calculate_pivot_points(df_price)
        save_pivot_points(df_pivot, interval)
        logging.info(f"{interval}ピボットポイントの計算と保存が完了しました")
    
    print("ピボットポイントの計算と保存が完了しました。")

if __name__ == "__main__":
    main()
