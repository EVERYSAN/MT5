import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

def load_data_from_db(symbol, interval, db_path='data/eurusd_trading.db'):
    """
    SQLiteデータベースから価格データを読み込みます。
    
    Args:
        symbol (str): シンボル名
        interval (str): データの間隔（'15m' または '1h'）
        db_path (str): データベースのパス
    
    Returns:
        pd.DataFrame: 読み込まれたデータフレーム
    """
    try:
        conn = sqlite3.connect(db_path)
        query = f"""
        SELECT timestamp, open, high, low, close, volume
        FROM price_data
        WHERE symbol = '{symbol}' AND interval = '{interval}'
        ORDER BY timestamp ASC
        """
        df = pd.read_sql_query(query, conn, parse_dates=['timestamp'], index_col='timestamp')
        conn.close()
        return df
    except Exception as e:
        print(f"データベースからの読み込み中にエラーが発生しました: {e}")
        return pd.DataFrame()

def visualize_price_data(df, symbol, interval):
    """
    価格データを可視化します。
    
    Args:
        df (pd.DataFrame): 可視化するデータフレーム
        symbol (str): シンボル名
        interval (str): データの間隔（'15m' または '1h'）
    """
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['close'], label='Close Price', color='blue')
    plt.title(f'{symbol} Close Prices ({interval})')
    plt.xlabel('Timestamp')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    SYMBOL = 'EURUSD'
    INTERVAL = '15m'  # または '1h'
    df = load_data_from_db(SYMBOL, INTERVAL)
    if not df.empty:
        visualize_price_data(df, SYMBOL, INTERVAL)
    else:
        print("データが存在しません")
