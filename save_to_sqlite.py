import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text


def save_price_data_to_db(df, symbol, interval, db_path='data/eurusd_trading.db'):
    try:
        engine = create_engine(f'sqlite:///{db_path}')
        df['symbol'] = symbol
        df['interval'] = interval
        df.reset_index(inplace=True)
        
        # データ型の変換
        for column in df.select_dtypes(include=['uint64']).columns:
            df[column] = df[column].astype('int64')
        df['symbol'] = df['symbol'].astype(str)
        df['interval'] = df['interval'].astype(str)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # データ型の再確認
        print(f"Data types after conversion for interval {interval}:")
        print(df.dtypes)
        
        # Insert each row individually
        conn = engine.connect()
        for index, row in df.iterrows():
            try:
                row_dict = row.to_dict()
                insert_stmt = text(f'''
                    INSERT OR IGNORE INTO price_data (timestamp, open, high, low, close, volume, symbol, interval)
                    VALUES (:timestamp, :open, :high, :low, :close, :volume, :symbol, :interval)
                ''')
                conn.execute(insert_stmt, row_dict)  # 修正箇所
            except Exception as e:
                print(f"Error inserting row {index}: {e}")
        conn.close()
        
        print(f"{interval}データをSQLiteデータベースに保存しました")
    except Exception as e:
        print(f"SQLiteへの保存中にエラーが発生しました: {e}")
