import sqlite3
import pandas as pd

def load_filtered_levels(symbol, interval, db_path='data/eurusd_trading.db'):
    """
    SQLiteデータベースからフィルタリングされた価格レベルを読み込みます。

    Args:
        symbol (str): シンボル名
        interval (str): データの間隔（'daily' または 'weekly'）
        db_path (str): データベースのパス

    Returns:
        list: フィルタリングされた価格レベルのリスト
    """
    try:
        conn = sqlite3.connect(db_path)
        query = f"""
        SELECT level
        FROM filtered_price_levels
        WHERE symbol = '{symbol}' AND interval = '{interval}'
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df['level'].tolist()
    except Exception as e:
        print(f"データベースからの読み込み中にエラーが発生しました: {e}")
        return []

def combine_levels(daily_levels, weekly_levels):
    """
    日足と週足のサポート・レジスタンスラインを統合します。

    Args:
        daily_levels (list): 日足の価格レベル
        weekly_levels (list): 週足の価格レベル

    Returns:
        list: 統合された価格レベルのリスト
    """
    combined = sorted(list(set(daily_levels + weekly_levels)))
    return combined

def save_combined_levels(combined_levels, symbol, db_path='data/eurusd_trading.db'):
    """
    統合された価格レベルをSQLiteデータベースに保存します。

    Args:
        combined_levels (list): 統合された価格レベルのリスト
        symbol (str): シンボル名
        db_path (str): データベースのパス
    """
    try:
        conn = sqlite3.connect(db_path)
        for level in combined_levels:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO combined_price_levels (symbol, level)
                VALUES (?, ?)
            ''', (symbol, level))
        conn.commit()
        conn.close()
        print("統合された価格レベルをデータベースに保存しました")
    except Exception as e:
        print(f"SQLiteへの保存中にエラーが発生しました: {e}")

def setup_combined_price_levels_table(db_path='data/eurusd_trading.db'):
    """
    combined_price_levels テーブルを作成します。

    Args:
        db_path (str): データベースのパス
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS combined_price_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            level REAL
        )
        ''')
        conn.commit()
        conn.close()
        print("combined_price_levels テーブルを作成しました")
    except Exception as e:
        print(f"SQLiteへの接続中にエラーが発生しました: {e}")

def main():
    SYMBOL = 'EURUSD'
    db_path = 'data/eurusd_trading.db'
    
    # combined_price_levels テーブルのセットアップ
    setup_combined_price_levels_table(db_path)
    
    # フィルタリングされた価格レベルの読み込み
    # ここでは filter_levels_with_rsi.py で保存された filtered_price_levels テーブルを使用
    daily_levels = load_filtered_levels(SYMBOL, 'daily', db_path)
    weekly_levels = load_filtered_levels(SYMBOL, 'weekly', db_path)
    
    # 水平線の統合
    combined_levels = combine_levels(daily_levels, weekly_levels)
    print(f"統合された価格レベル: {combined_levels}")
    
    # データベースに保存
    save_combined_levels(combined_levels, SYMBOL, db_path)

if __name__ == "__main__":
    main()
