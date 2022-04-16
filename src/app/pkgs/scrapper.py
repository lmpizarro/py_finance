from audioop import reverse
from os import sync
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
    def filter(table):
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


if __name__ == '__main__':
    symbols = TickerScrappers.sp500b_slickcharts()
    print(symbols)

    symbols = TickerScrappers.nasdaq100_slickcharts()
    print(symbols)
    TickerScrappers.resp_text(TickerScrappers.nasdaq_url)