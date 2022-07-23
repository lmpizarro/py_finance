from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import requests
from enum import Enum

__all__ = ['TickerScrappers'] 

class Indexs(Enum):
    NASDAQ100 = 'NASDAQ100'
    SP500 = 'SP500'
    DOWJONES = 'DOWJONES'

class TickerScrappers:
    nasdaq_url = 'https://www.slickcharts.com/nasdaq100'
    sp500_url = 'https://www.slickcharts.com/sp500'
    dowjones_url = 'https://www.slickcharts.com/dowjones'

    @staticmethod
    def resp_text(url):
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, features='lxml')
        table = soup.find('table', {'class': 'table table-hover table-borderless table-sm'})
        return table 

    @staticmethod
    def nasdaq100_slickcharts():

        table = TickerScrappers.resp_text(TickerScrappers.nasdaq_url)
        return TickerScrappers.filter(table)

    @staticmethod
    def filter(table) -> List[Dict[str,Any]]:
        tickers = set()
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[1]
            weight = row.findAll('td')[3]
            price = float(''.join(row.findAll('td')[4].text.strip().split(',')))
            symbol = ticker.a.get('href').split('/')[2]
            tickers.add((symbol, float(weight.text), price))

        tickers = list(tickers)
        tickers.sort(key=lambda tup: tup[1], reverse=True)
        tickers = [{'ticker': t[0], 'weight': t[1], 'price': t[2]} for t in tickers]
        return tickers


    @staticmethod
    def sp500b_slickcharts():
        
        table = TickerScrappers.resp_text(TickerScrappers.sp500_url)

        return TickerScrappers.filter(table)

    @staticmethod
    def dow_slickcharts():
        
        table = TickerScrappers.resp_text(TickerScrappers.dowjones_url)

        return TickerScrappers.filter(table)

    @staticmethod
    def cedears(dividend_freq: Optional[str]=None):
        url = 'https://www.comafi.com.ar/2254-CEDEAR-SHARES.note.aspx'
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text,  features="lxml")
        table = soup.find('table')

        tickers = {}
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[3].text
            # ticker = row.findAll('td')[1]
            # ticker = ticker.a.get('href').split('/')[2]
            div_freq = row.findAll('td')[8].text
            ratio = row.findAll('td')[7].text
            if ticker not in tickers:
                tickers[ticker] = {'ticker': ticker,
                                   'weight': 0,
                                   'price': 0,
                                   'div_freq': div_freq,
                                   'ratio': ratio}
        
        return [tickers[e] for e in tickers]

    @staticmethod
    def cedear_in_sp500():
        sp500 = TickerScrappers.sp500b_slickcharts()
        cedear = TickerScrappers.cedears()

        sp500s = set()
        sp500d = {}
        for e in sp500:
            sp500s.add(e['ticker'])
            sp500d[e['ticker']] = e

        cedears = set()
        cedeard = {}
        for e in cedear:
            cedears.add(e['ticker'])
            cedeard[e['ticker']] = e

        intersect = cedears.intersection(sp500s)

        list_cedears = []
        for e in intersect:
            extra_kv = {k:cedeard[e][k] for k in ['div_freq', 'ratio'] }
            sp500d[e].update(extra_kv)
            list_cedears.append(sp500d[e])

        list_cedears.sort(key=lambda tup: tup['weight'], reverse=True)
        return(list_cedears)

     
    @staticmethod
    def filter_cedears(dividend_freq: Optional[str]=None):

        all_freq_div = ['Annual', 'Quarterly', 'Semi-annual', 'None', 'Irreg', '-']

        if dividend_freq not in all_freq_div:
            return []

        l = TickerScrappers.cedear_in_sp500()
        dividendQ = []
        for c in l:
            if c['div_freq'] == dividend_freq:
                dividendQ.append(c)

        return dividendQ
