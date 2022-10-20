import pandas as pd

from flight_control import DataLogger

def test_logger():
    logger = DataLogger('test.csv', ['test', 'data'])
    logger.log_data({'test': 1, 'data': 2})
    logger.log_data({'test': 3, 'data': 5})
    
    test_frame = pd.DataFrame({'test': [1, 3], 'data': [2, 5]})
    file_frame = pd.read_csv('test.csv')
    assert test_frame[['test','data']].equals(file_frame[['test','data']])
