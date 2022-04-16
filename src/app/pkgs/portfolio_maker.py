from pkgs.scrapper import TickerScrappers, Indexs
from pkgs.portfolio import PortfolioComponent, PortofolioDescription
from datetime import datetime, timedelta


__all__ = ['MakerScrapper']


class MakerScrapper:

    def __init__(self, index: Indexs) -> None:
        self.index = index

    def base_portfolio(self, limit=20):
        if self.index == Indexs.DOWJONES:
            data = TickerScrappers.dow_slickcharts()
        elif self.index == Indexs.NASDAQ100:
            data = TickerScrappers.nasdaq100_slickcharts()
        elif self.index == Indexs.SP500:
            data = TickerScrappers.sp500b_slickcharts()
        
        list_components = []
        for e in data[:limit]:
            pc: PortfolioComponent = PortfolioComponent()
            pc.symbol = e['ticker']
            list_components.append(pc)

        now = datetime.now()
        one_year = timedelta(days=365)
        start_period = now - one_year
 

        p_desc = PortofolioDescription(components=list_components,
                                       name=f'base porfolio {self.index}',
                                       start_period=str(start_period.strftime('%Y-%m-%d')))

        return p_desc

