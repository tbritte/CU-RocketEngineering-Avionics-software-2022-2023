import pandas as pd
import time

from ._typing import DFData

class DataLogger():
    def __init__(self, file_name: str, columns:list, start_time:float = time.time()):
        self.file_name = file_name
        self.START_TIME = start_time
        
        self.df = pd.DataFrame(columns=columns)
        self.df.to_csv(file_name, header=True)
    
    def log_data(self, data: DFData) -> None:
        """Logs the data to a CSV File.
        
        Logs the data into the associated columns declared when the class was initialized. Uses
        how many seconds have passed since the start of the program as the index of the data.

        Args:
            data (DFData): Takes in any datatype compatible with pandas DataFrame to be appended to the CSV file.
        """
        df = pd.DataFrame(data, columns=self.df.columns, index=[time.time() - self.START_TIME])
        df.to_csv(self.file_name, mode='a', header=False)
    
    def get_pandas_data(self) -> pd.DataFrame:
        """Gets the pandas DataFrame object from the CSV file and returns it.

        Returns:
            pd.DataFrame: The DataFrame object stored in the CSV file.
        """
        return pd.read_csv(self.file_name)