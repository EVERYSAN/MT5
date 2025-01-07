# scripts/extract_support_resistance.py

import sqlite3
import pandas as pd
import os
import logging

# ログディレクトリとファイル名を設定
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'support_resistance_extraction.log')

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

def fetch_pivot_points(interval):
    """
    データベースから指定した間隔のピボットポイントを取得します。
    
    Args:
        interval (str): データの間隔（'daily' または 'weekly'）
    
    Returns:
        pd.DataFrame: ピボットポイントデータ
    """
    conn = sqlite3.connect(DB_PATH)
    query = f"""
    SELECT timestamp, Pivot, Support1, Resistance1, Support2, Resistance2
    FROM pivot_points
    WHERE interval = '{interval}'
    ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, parse_dates=['timestamp'])
    conn.close()
    return df

def save_support_resistance(df_sr, interval):
    """
    抽出したサポートラインとレジスタンスラインをデータベースに保存します。
    
    Args:
        df_sr (pd.DataFrame): サポートラインとレジスタンスラインを含むデータフレーム
        interval (str): データの間隔（'daily' または 'weekly'）
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for _, row in df_sr.iterrows():
        try:
            # Support1
            cursor.execute('''
                INSERT OR REPLACE INTO price_levels 
                (timestamp, symbol, interval, level, type)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'EURUSD',
                interval,
                row['Support1'],
                'Support1'
            ))
            # Support2
            cursor.execute('''
                INSERT OR REPLACE INTO price_levels 
                (timestamp, symbol, interval, level, type)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'EURUSD',
                interval,
                row['Support2'],
                'Support2'
            ))
            # Resistance1
            cursor.execute('''
                INSERT OR REPLACE INTO price_levels 
                (timestamp, symbol, interval, level, type)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'EURUSD',
                interval,
                row['Resistance1'],
                'Resistance1'
            ))
            # Resistance2
            cursor.execute('''
                INSERT OR REPLACE INTO price_levels 
                (timestamp, symbol, interval, level, type)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'EURUSD',
                interval,
                row['Resistance2'],
                'Resistance2'
            ))
        except Exception as e:
            logging.error(f"Error inserting price level for {row['timestamp']}: {e}")
            print(f"Error inserting price level for {row['timestamp']}: {e}")
            # エラー発生時にスクリプトを停止する場合は以下をコメント解除
            # raise e
    
    conn.commit()
    conn.close()
    logging.info(f"{interval}データのサポートラインとレジスタンスラインをデータベースに保存しました")

def main():
    intervals = ['daily', 'weekly']
    for interval in intervals:
        logging.info(f"{interval}データのサポートラインとレジスタンスライン抽出を開始します")
        df_pivot = fetch_pivot_points(interval)
        if df_pivot.empty:
            logging.warning(f"{interval}データのピボットポイントがデータベースに存在しません")
            continue
        
        # サポートラインとレジスタンスラインの抽出
        df_sr = df_pivot[['timestamp', 'Support1', 'Support2', 'Resistance1', 'Resistance2']].copy()
        
        # データベースへの保存
        save_support_resistance(df_sr, interval)
        logging.info(f"{interval}データのサポートラインとレジスタンスライン抽出と保存が完了しました")
    
    print("サポートラインとレジスタンスラインの抽出と保存が完了しました。")

if __name__ == "__main__":
    main()
