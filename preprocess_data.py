from scipy import stats
import numpy as np
import pandas as pd

def preprocess_price_data(df):
    """
    価格データの前処理を行います。
    
    Args:
        df (pd.DataFrame): 前処理するデータフレーム
    
    Returns:
        pd.DataFrame: 前処理済みデータフレーム
    """
    try:
        # 欠損値の補完（前値で補完）
        df = df.ffill()
        
        # 異常値の処理（Zスコアによる除外）
        z_scores = stats.zscore(df[['open', 'high', 'low', 'close', 'volume']])
        abs_z_scores = np.abs(z_scores)
        filtered_entries = (abs_z_scores < 3).all(axis=1)
        df = df[filtered_entries]
        
        return df
    except Exception as e:
        print(f"前処理中にエラーが発生しました: {e}")
        return df
