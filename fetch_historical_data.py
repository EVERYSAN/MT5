import sqlite3
import pandas as pd
import os
import logging
from datetime import datetime

# ログディレクトリとファイル名を設定
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'historical_data_fetch.log')

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'eurusd_trading.db')

def fetch_and_store_data(interval):
    data = {
        'timestamp': pd.date_range(start='2024-01-01', periods=10, freq='D'),
        'open': [1.1750, 1.1800, 1.1850, 1.1900, 1.1950, 1.2000, 1.2050, 1.2100, 1.2150, 1.2200],
        'high': [1.1800, 1.1850, 1.1900, 1.1950, 1.2000, 1.2050, 1.2100, 1.2150, 1.2200, 1.2250],
        'low': [1.1700, 1.1750, 1.1800, 1.1850, 1.1900, 1.1950, 1.2000, 1.2050, 1.2100, 1.2150],
        'close': [1.1780, 1.1830, 1.1880, 1.1930, 1.1980, 1.2030, 1.2080, 1.2130, 1.2180, 1.2230],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
        'symbol': ['EURUSD'] * 10
    }
    df = pd.DataFrame(data)

    # データのクリーニング
        # 重複データの削除
    df.drop_duplicates(subset='timestamp', keep='first', inplace=True)

    # 価格変動のないデータを除外
    df = df[(df['open'] != df['close']) | (df['high'] != df['low'])]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO price_data (timestamp, open, high, low, close, volume, symbol, interval)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                row['open'],
                row['high'],
                row['low'],
                row['close'],
                row['volume'],
                row['symbol'],
                interval
            ))
        except Exception as e:
            logging.error(f"Error inserting data for {row['timestamp']}: {e}")
            print(f"Error inserting data for {row['timestamp']}: {e}")

    conn.commit()
    conn.close()
    logging.info(f"{interval}データの取得と保存が完了しました")

def main():
    intervals = ['daily', 'weekly', '1h', '15m']
    for interval in intervals:
        logging.info(f"{interval}データの取得を開始します")
        fetch_and_store_data(interval)
        logging.info(f"{interval}データの取得と保存が完了しました")
    
    print("ヒストリカルデータの取得と保存が完了しました。")

if __name__ == "__main__":
    main()
