import pandas as pd

from flight_control import Logger

def test_logger():
    logger = Logger('test.csv', ['test', 'data'])
    logger.log_data({'test': 1, 'data': 2})
    print(pd.read_csv('test.csv'))