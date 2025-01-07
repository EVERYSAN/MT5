import sqlite3
import pandas as pd
from ta.momentum import RSIIndicator
import os

def load_price_data(symbol, interval, db_path='data/eurusd_trading.db'):
    """
    SQLiteデータベースから価格データを読み込みます。

    Args:
        symbol (str): シンボル名
        interval (str): データの間隔（'15m' または '1h' など）
        db_path (str): データベースのパス

    Returns:
        pd.DataFrame: 読み込まれた価格データフレーム
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

def calculate_rsi(df, window=14):
    """
    RSIを計算します。

    Args:
        df (pd.DataFrame): 価格データフレーム
        window (int): RSIの計算ウィンドウ

    Returns:
        pd.Series: RSI値のシリーズ
    """
    rsi = RSIIndicator(close=df['close'], window=window)
    return rsi.rsi()

def filter_levels_with_rsi(rsi, levels, rsi_threshold=50):
    """
    RSIを用いてサポート・レジスタンスラインをフィルタリングします。

    Args:
        rsi (pd.Series): RSI値のシリーズ
        levels (list): 抽出された価格レベルのリスト
        rsi_threshold (float): RSIの閾値

    Returns:
        list: フィルタリングされた価格レベルのリスト
    """
    latest_rsi = rsi.iloc[-1]

    if latest_rsi > rsi_threshold:
        # RSIが高い場合、レジスタンスラインを重視
        filtered_levels = [level for level in levels if level > current_price]
    elif latest_rsi < rsi_threshold:
        # RSIが低い場合、サポートラインを重視
        filtered_levels = [level for level in levels if level < current_price]
    else:
        filtered_levels = levels

    return filtered_levels

def load_price_levels(symbol, interval, db_path='data/eurusd_trading.db'):
    """
    SQLiteデータベースから価格レベルを読み込みます。

    Args:
        symbol (str): シンボル名
        interval (str): データの間隔（'daily' または 'weekly'）
        db_path (str): データベースのパス

    Returns:
        list: 読み込まれた価格レベルのリスト
    """
    try:
        conn = sqlite3.connect(db_path)
        query = f"""
        SELECT level
        FROM price_levels
        WHERE symbol = '{symbol}' AND interval = '{interval}'
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df['level'].tolist()
    except Exception as e:
        print(f"データベースからの読み込み中にエラーが発生しました: {e}")
        return []

def main():
    SYMBOL = 'EURUSD'
    INTERVAL = '1h'  # 例として1時間足を使用
    db_path = 'data/eurusd_trading.db'
    
    # 価格データの読み込み
    df = load_price_data(SYMBOL, INTERVAL, db_path)
    if df.empty:
        print("価格データが存在しません")
        return
    
    # RSIの計算
    df['RSI'] = calculate_rsi(df, window=14)
    
    # 最新の価格
    current_price = df['close'].iloc[-1]
    
    # ピボットポイントから価格レベルの読み込み
    daily_levels = load_price_levels(SYMBOL, 'daily', db_path)
    weekly_levels = load_price_levels(SYMBOL, 'weekly', db_path)
    combined_levels = sorted(list(set(daily_levels + weekly_levels)))
    
    # RSIによるフィルタリング
    filtered_levels = filter_levels_with_rsi(df['RSI'], combined_levels, rsi_threshold=50)
    
    # フィルタリングされた価格レベルを表示
    print(f"フィルタリングされた価格レベル: {filtered_levels}")

if __name__ == "__main__":
    main()
