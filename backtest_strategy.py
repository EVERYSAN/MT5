import sqlite3
import pandas as pd
import backtrader as bt
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'eurusd_trading.db')

class EnhancedSmaCrossStrategy(bt.Strategy):
    params = (
        ('sma_short_period', 50),
        ('sma_long_period', 200),
        ('atr_period', 14),
        ('risk_percent', 0.01),
        ('bb_period', 50),
        ('bb_dev', 2.1),
    )

    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_short_period)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_long_period)
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.params.atr_period)
        self.boll = SafeBollingerBands(period=self.params.bb_period, devfactor=self.params.bb_dev)
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.sma_short > self.sma_long:
                self.order = self.buy()
            elif self.sma_short < self.sma_long:
                self.order = self.sell()
        else:
            if self.position.size > 0 and self.data.close[0] < self.boll.bot[0]:
                self.close()
            elif self.position.size < 0 and self.data.close[0] > self.boll.top[0]:
                self.close()

class SafeBollingerBands(bt.Indicator):
    lines = ('mid', 'top', 'bot',)
    params = (('period', 20), ('devfactor', 2.0))

    def __init__(self):
        self.ma = bt.indicators.SMA(self.data, period=self.p.period)
        self.sd = bt.indicators.StandardDeviation(self.data, period=self.p.period)

    def next(self):
        sd_value = self.sd[0] if self.sd[0] != 0 else 0.00001
        self.lines.mid[0] = self.ma[0]
        self.lines.top[0] = self.ma[0] + (self.p.devfactor * sd_value)
        self.lines.bot[0] = self.ma[0] - (self.p.devfactor * sd_value)

def fetch_price_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT DISTINCT timestamp, open, high, low, close, volume
    FROM price_data
    WHERE interval = 'daily'
    ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, parse_dates=['timestamp'])
    conn.close()

    # データクリーニング
    df.drop_duplicates(subset='timestamp', keep='first', inplace=True)
    df = df[(df['open'] != df['close']) | (df['high'] != df['low'])]

    return df

def main():
    cerebro = bt.Cerebro()
    df = fetch_price_data()
    if len(df) < 200:
        raise ValueError("データポイントが不足しています。")

    data_feed = bt.feeds.PandasData(
        dataname=df,
        datetime='timestamp',
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume'
    )
    cerebro.adddata(data_feed)

    cerebro.addstrategy(EnhancedSmaCrossStrategy)
    cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    main()
