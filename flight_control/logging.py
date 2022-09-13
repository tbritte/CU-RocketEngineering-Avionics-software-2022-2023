import pandas as pd
import time

from _typing import DFData

class Logger():
    def __init__(self, file_name: str, columns:list, start_time:float = time.time()):
        self.file_name = file_name
        self.START_TIME = start_time
        
        self.df = pd.DataFrame(columns=columns)
        self.df.to_csv(file_name, header=True)
    
    def log_data(self, data: DFData) -> None:
        df = pd.DataFrame(data, columns=self.df.columns, index=[time.time() - self.START_TIME])
        df.to_csv(self.file_name, mode='a', header=False)
    
    def get_pandas_data(self) -> pd.DataFrame:
        return pd.read_csv(self.file_name)