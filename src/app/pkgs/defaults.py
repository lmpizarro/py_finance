from datetime import datetime, timedelta

__all__ = ['Defaults']

class Defaults:
    @staticmethod
    def end_date()->str:
        now = datetime.now()
        end_date = now.strftime('%Y-%m-%d')

        return end_date

    @staticmethod
    def start_date()->str:
        now = datetime.now()
        one_year = timedelta(days=365)
        start_date = now - one_year
        start_date = start_date.strftime('%Y-%m-%d')

        return start_date


