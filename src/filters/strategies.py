import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import pandas as pd
import numpy as np


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

def return_analysis(df):

    ds = df.to_frame(name='Adj Close')

    ds['log_return'] = np.log(ds['Adj Close']/ds['Adj Close'].shift(1))
    daily_log_returns = ds['log_return'].mean()
    daily_std = ds['log_return'].std()
    annual_log_returns = ds['log_return'].mean() * 250
    log_return_y = ds.log_return.tail(60)
    day_log_return_y = log_return_y.mean()
    annual_log_return_y = day_log_return_y * 250
    delta_ann_log_return = annual_log_return_y > annual_log_returns

    neg = ds['log_return'][ds['log_return'] < 0]
    mean_neg = neg.mean()
    std_neg = neg.std()

    min_2sigma = daily_log_returns - 2 * daily_std
    max_2sigma = daily_log_returns + 2 * daily_std


    # print(t, daily_log_returns, annual_log_returns, mean_neg, limit_, 
    #       round(delta_ann_log_return, 4))

    # if delta_ann_log_return: 
    #     print(t, annual_log_returns, annual_log_return_y)
    condition = 'NOT KNO'
    if annual_log_return_y < 0 and annual_log_returns < 0:
       condition = 'NEG NEG'

    if annual_log_return_y < 0 and annual_log_returns > 0:
        condition =  'NEG POS'

    if annual_log_return_y > 0 and annual_log_returns > 0:
        condition = 'POS POS'

    if annual_log_return_y > 0 and annual_log_returns < 0:
        condition = 'POS NEG'


    return(t, condition, round(min_2sigma, 4), 
           round(100*annual_log_return_y,2))

if __name__ == '__main__':
    symbols_a = ['GOLD', 'BRK-B', 'T', 'GILD', 'GSK', 'HON',
                 'SONY', 'SQ', 'SPOT', 'SNA', 'SYY', 'TS', 
                 'TX', 'ETSY', 'TWTR', 'GLOB', 'FDX','EBAY','BA', 
                 'GE', 'BIIB', 'UNH', 'ORCL', 'LLY', 'ABT', 'AZN', 
                 'LMT', 'V', 'DIS', 'TMO',   'MO',  'ADP', 'ACN', 'SBUX', 
                 'XOM', 'CVX', 'BAC', 'SHEL', 'RTX',  'MA', 'BABA',  
                 'CRM', 'SYY', 'VOD', 'PYPL', 'TSLA']
    # test_strategy_01(to_sell)

    BRB = ["ABBV", "ADBE", "ADI", "AMAT", "AMGN", "AVGO", "CAT",
           "COST", "GGAL", "GOOGL", "JNJ", "MELI", "MMM",
           "NKE", "NVS", "PG", "QCOM", "TM", "TSM", "VZ", "WBA",
           "WMT", "YPF"]

    BRA = ["AAPL", "AMD", "AMZN", "CSCO", "DE", "FB", "HD", 
           "IBM", "INTC", "JPM", "KO", "MSFT", "NVDA", "PEP", 
           "PFE", "TGT", "TXN", 
    ]

    BRAZ = ['VALE', 'PBR', 'ITUB', 'BBD', 'RIO', 'ABEV', 'BSBR', 'SID',
            'CBD', 'GGB', 'VIV', 'UGP', 'SAN', 'BBVA', 'TEF',
            'SIE', 'DMLRY']

    BRB.extend(BRA)
    symbols = symbols_a


    df = yf.download(symbols, '2016-1-1')['Adj Close']
    for t in symbols:

        r_an = return_analysis(df[t])
        if r_an[3] > 0:
            da = yf.Ticker(t)

            divs = da.dividends.tail(1)
            if len(divs):
                sdiv = divs[0]
                close = df[t].tail(1)[0]
                pcdivclose = round(100 * sdiv / close,2)
                print(r_an, pcdivclose, divs.index[0].to_pydatetime().strftime("%Y/%m/%d"))

