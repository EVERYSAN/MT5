import sqlite3

def check_intervals(db_path='data/eurusd_trading.db'):
    """
    SQLiteデータベース内のprice_dataテーブルに存在するインターバルを確認します。
    
    Args:
        db_path (str): データベースのパス
    
    Returns:
        list: 存在するインターバルのリスト
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = "SELECT DISTINCT interval FROM price_data"
        cursor.execute(query)
        intervals = cursor.fetchall()
        conn.close()
        return [interval[0] for interval in intervals]
    except Exception as e:
        print(f"データベースへの接続中にエラーが発生しました: {e}")
        return []

def main():
    intervals = check_intervals()
    if intervals:
        print("データベースに存在するインターバル:")
        for interval in intervals:
            print(f"- {interval}")
    else:
        print("price_dataテーブルにデータが存在しません。")

if __name__ == "__main__":
    main()
