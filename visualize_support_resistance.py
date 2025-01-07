# scripts/visualize_support_resistance.py

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# SQLiteデータベースのパス
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'eurusd_trading.db')

def fetch_price_and_levels(interval):
    """
    価格データとサポート・レジスタンスラインを取得します。
    
    Args:
        interval (str): データの間隔（'daily' または 'weekly'）
    
    Returns:
        pd.DataFrame: 価格データと水準線データ
    """
    conn = sqlite3.connect(DB_PATH)
    price_query = f"""
    SELECT timestamp, close
    FROM price_data
    WHERE interval = '{interval}'
    ORDER BY timestamp ASC
    """
    price_df = pd.read_sql_query(price_query, conn, parse_dates=['timestamp'])
    
    levels_query = f"""
    SELECT timestamp, level, type
    FROM price_levels
    WHERE interval = '{interval}'
    ORDER BY timestamp ASC
    """
    levels_df = pd.read_sql_query(levels_query, conn, parse_dates=['timestamp'])
    conn.close()
    
    return price_df, levels_df

def plot_levels(price_df, levels_df, interval):
    """
    価格データとサポート・レジスタンスラインをプロットします。
    
    Args:
        price_df (pd.DataFrame): 価格データ
        levels_df (pd.DataFrame): サポート・レジスタンスラインデータ
        interval (str): データの間隔（'daily' または 'weekly'）
    """
    plt.figure(figsize=(14,7))
    plt.plot(price_df['timestamp'], price_df['close'], label='Close Price', color='blue')
    
    # 各水準線をプロット
    for _, row in levels_df.iterrows():
        if row['type'] == 'Support1':
            plt.axhline(y=row['level'], color='green', linestyle='--', label='Support1')
        elif row['type'] == 'Support2':
            plt.axhline(y=row['level'], color='lightgreen', linestyle='--', label='Support2')
        elif row['type'] == 'Resistance1':
            plt.axhline(y=row['level'], color='red', linestyle='--', label='Resistance1')
        elif row['type'] == 'Resistance2':
            plt.axhline(y=row['level'], color='orange', linestyle='--', label='Resistance2')
    
    plt.title(f'EURUSD {interval.capitalize()} Close Price with Support and Resistance Lines')
    plt.xlabel('Timestamp')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    intervals = ['daily']  # 'weekly' を追加したい場合はリストに含めます
    for interval in intervals:
        price_df, levels_df = fetch_price_and_levels(interval)
        plot_levels(price_df, levels_df, interval)

if __name__ == "__main__":
    main()
