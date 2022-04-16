import setup
from pkgs.portfolio_maker import MakerScrapper, Indexs

if __name__ == '__main__':

    m = MakerScrapper(Indexs.SP500)
    m.base_portfolio()