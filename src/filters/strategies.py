import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import pandas as pd



def strategy_01(ds:pd.Series, 
                  key:str='Adj Close', 
                  fs=250, 
                  ffast=6, 
                  fslow=3):
                  
    df = ds.to_frame(name=key)

    sos_fast = signal.butter(1, ffast, 'lp', fs=fs, output='sos')
    sos_slow = signal.butter(1, fslow, 'lp', fs=fs, output='sos')
    df['fast_ccl'] = signal.sosfiltfilt(sos_fast, df[key])
    df['slow_ccl'] = signal.sosfiltfilt(sos_slow, df[key])
    df['bp'] = df.fast_ccl - df.slow_ccl
    df['long'] = df.bp >= 0.0
    df['short'] = df.bp < 0
    df['buy_long'] = (df.long - df.long.shift(1)) > 0
    df['buy_short'] = (df.short - df.short.shift(1)) > 0

    return df


def strategy_02(ds:pd.Series, 
                key='Adj Close', 
                fs=256, 
                bp=[4,8]):
 
    df = ds.to_frame(name=key)
    sos_bp = signal.butter(1, bp, 'bandpass', fs=fs, output='sos')
    df['bp'] = signal.sosfiltfilt(sos_bp, df[key])
    df['long'] = df.bp >= 0.0
    df['buy_long'] = (df.long - df.long.shift(1)) > 0
    
    an_sig = signal.hilbert(df['bp'])
    df['envelope'] = np.abs(an_sig)

    """
    from sklearn.linear_model import LinearRegression
    df['phase'] = np.unwrap(np.angle(an_sig))
    df['frequency'] = df['phase'].diff() / ((2.0*np.pi) * fs)
    X = np.asarray(range(0, len(df.phase))).reshape(-1, 1)
    reg = LinearRegression().fit(X, df['phase'])
    pred = reg.predict(X)
    df.phase = df.phase - pred
    """

    df.dropna(inplace=True)

    df['sell'] = (df.envelope - df.bp)
    df['buy'] = (df.envelope + df.bp)

    return df

def test_strategy_02(symbols):

    df = yf.download(symbols, '2020-7-1')['Adj Close']
    df.dropna(inplace=True)

    fs = 252
    for t in symbols:
        dff = strategy_02(df[t], bp=[0.035*fs, 0.07*fs], fs=fs)
        b01 = round(dff.buy.tail(2)[1] - dff.buy.tail(2)[0], 4)
        print(f'{t} SELL {round(dff.sell.tail(1)[0],2)}, '
              f'BUY {round(dff.buy.tail(1)[0],2)}, '
              f'  {b01} ')
        plt.grid()
        plt.plot(dff.buy)
        plt.plot(-dff.sell)
        plt.show()

def test_strategy_01(symbols):

    df = yf.download(symbols, '2020-7-1')['Adj Close']
    df.dropna(inplace=True)

    fs = 252
    for t in symbols:
        df_out = strategy_01(df[t], fs=fs)
        print(f'{t} long {df_out.long.tail(1)[0]}')

        plt.grid()
        plt.plot(np.asarray(df_out.buy_long), 'g')
        plt.plot(np.asarray(df_out.buy_short), 'r')
        plt.show()


if __name__ == '__main__':
    symbols_a = ['AAPL', 'AMZN', 'JPM', 'KO', 'DE', 'TSLA', 'TGT',
                'FB', 'GOLD', 'INTC', 'IBM', 'MSFT', 'TXN', 'NVDA', 'PYPL']

    symbols_b = ['WBA', 'GOOGL', 'AMAT', 'ADI', 'AMGN', 'YPF', 'GGAL', 
                 'ABBV', 'ADBE', 'AVGO', 'CAT', 'COST', 'JNJ', 'MELI', 
                 'MMM', 'NKE', 'NVS', 'PG', 'QCOM', 'TM', 'VZ', 
                 'TSM', 'WMT']

    symbols_d = ['SONY', 'SQ', 'SPOT', 'SNA', 'SYY', 'SBUX', 'VOD', 'TS', 
                 'TX', 'GILD', 'ETSY', 'TWTR', 'GLOB', 'FDX','EBAY','BA', 
                 'GE', 'BIIB', 'GSK', 'HON', 'XOM', 'CVX']

    symbols_c = ['UNH', 'JPM', 'XOM', 'CVX', 'HD', 'BAC', 'PFE', 'LLY', 'ORCL', 
               'PEP', 'ABT', 'SHEL', 'AZN', 'LMT', 'RTX', 'V', 'BRK-B', 'MA',
               'DIS', 'BABA', 'TMO', 'ACN', 'CRM', 'T', 'AMD', 'MO', 'ADP']

    to_buy = ['HD', 'SHEL', 'AZN', 'AMD', 'SYY', 'VOD']

    to_sell = ['PYPL', 'TSLA', 'MSFT', 'TXN']
    test_strategy_01(to_sell)


